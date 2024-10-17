import os
import time
from urllib.parse import urlparse

import cv2
import requests
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._pages.chromium_frame import ChromiumFrame

from app import logging_config

logger = logging_config.get_logger(__name__)
# 图片保存目录
image_save_dir = "../image"
slide_icon_path = "../image/slide_icon.png"

class Validator:
    """
    抖音滑块验证码验证器
    @author: lisanlai
    """
    @staticmethod
    def validate(frame: ChromiumFrame, bg_image_id: str, slide_image_id: str):
        """
        验证滑块验证码
        :param frame: 网页对象
        :param bg_image_id: 验证码背景图片元素ID, e.g: #captcha_verify_image
        :param slide_image_id: 缺口图片元素ID, e.g: #captcha-verify_img_slide
        :return: True or False
        """
        logger.info(f'开始验证验证码，当前页面={frame.url}')
        # 等待验证码图片加载完成

        # 定位背景图片和缺口图片元素
        bg_image_el = frame(f'#{bg_image_id}')
        slide_image_el = frame(f'#{slide_image_id}')

        if bg_image_el is None or slide_image_el is None:
            logger.info(f'找不到页面元素，bg_image_id={bg_image_id}, slide_image_id={slide_image_id}')
            return False

        # 读取元素的图片src
        bg_image_src = bg_image_el.attr('src')
        slide_image_src = slide_image_el.attr('src')
        logger.info(f'bg_image_src={bg_image_src}, slide_image_src={slide_image_src}')
        slide_image_loc = slide_image_el.rect.location
        # 返回：(50, 50)
        logger.info(f'缺口块的位置：{slide_image_loc}')

        # 生成存储路径
        bg_image_filename = Validator.extract_filename_from_url(bg_image_src)
        slide_image_filename = Validator.extract_filename_from_url(slide_image_src)
        bg_img_save_path = Validator.assemble_full_path(image_save_dir, bg_image_filename)
        slide_img_save_path = Validator.assemble_full_path(image_save_dir,slide_image_filename)

        # 开始下载背景图片和滑块图片
        Validator.download_image(bg_image_src, bg_img_save_path)
        Validator.download_image(slide_image_src, slide_img_save_path)
        # 延时0.5S
        time.sleep(0.5)

        # 计算缺口图片的坐标
        offset_x, offset_y = Validator.calculateLocation(bg_image_el,
                                                         slide_image_el,
                                                         bg_img_save_path,
                                                         slide_img_save_path)

        # 拖动滑块
        Validator.dragSlide(frame, offset_x, offset_y, f'#{slide_image_id}')
        time.sleep(0.5)
        return True

    @staticmethod
    def download_image(img_src: str, save_path: str, max_retries=3):
        """
        下载指定src的图片到指定路径
        :param img_src: 图片源地址
        :param save_path: 存储路径
        :param max_retries: 重试次数
        :return: True or False
        """
        # 检查文件是否已经存在
        if os.path.exists(save_path):
            logger.info(f"图片已经存在: {save_path}")
            return False
        # 重试次数
        retries = 0
        while retries < max_retries:
            try:
                # 发送 HTTP GET 请求
                logger.info(f'开始下载图片，图片地址={img_src}, 存储路径={save_path}')
                response = requests.get(img_src, stream=True)

                # 检查请求是否成功
                if response.status_code == 200:
                    # 确保保存路径的目录存在
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    # 以二进制写入模式打开文件
                    with open(save_path, 'wb') as file:
                        # 分块写入文件
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    logger.info(f"图片下载成功，存储路径: {save_path}")
                    return True
                else:
                    logger.info(f"下载图片失败. HTTP Status code: {response.status_code}")
                    return False
            except Exception as e:
                retries += 1
                logger.info(f"下载图片出错: {e}. 重试次数: {retries}/{max_retries}")
                if retries < max_retries:
                    time.sleep(1)  # 等待 2 秒后重试
                else:
                    logger.info("超过最大重试次数，下载失败。")
                    return False

    @staticmethod
    def calculateLocation(bg_img_el: ChromiumElement, slide_img_el: ChromiumElement, bg_img_path: str, slide_img_path: str):
        """
        计算缺口图片在背景图片里面的坐标
        :param bg_img_el 背景图片element
        :param slide_img_el 滑块图片element
        :param bg_img_path: 背景图片
        :param slide_img_path: 缺口图片
        :return:
        """
        print(f'开始计算缺口图片在背景图片里面的坐标, bg_img_path={bg_img_path}, slide_img_path={slide_img_path}')
        # 读取图片
        bg_img = cv2.imread(bg_img_path, cv2.IMREAD_COLOR)
        slide_img = cv2.imread(slide_img_path, cv2.IMREAD_COLOR)

        if bg_img is None or slide_img is None:
            logger.info(f'找不到图片，bg_img_path={bg_img_path}, slide_img_path={slide_img_path}')
            return False

        # 转换图片格式
        bg_edge_pic = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
        slide_edge_pic = cv2.cvtColor(slide_img, cv2.COLOR_BGR2GRAY)

        bg_edge = cv2.Canny(bg_edge_pic, 50, 100)
        slide_edge = cv2.Canny(slide_edge_pic, 50, 100)

        # 获取图片尺寸
        width, height = slide_img_el.rect.size
        logger.info(f'滑块图片元素的size，{width} x {height}')

        # 获取图片尺寸
        width1, height1 = bg_img_el.rect.size
        logger.info(f'背景图片元素的size，{width1} x {height1}')

        # 获取模板图像的高和宽
        th, tw = slide_edge_pic.shape[:2]
        logger.info(f'滑块图片：高={th}, 宽={tw}')

        # 获取背景图片的宽高
        th1, tw1 = bg_edge_pic.shape[:2]
        logger.info(f'背景图片：高={th1}, 宽={tw1}')

        # 缺口匹配
        result = cv2.matchTemplate(image=bg_edge, templ=slide_edge, method=cv2.TM_CCOEFF_NORMED)

        # result为匹配结果矩阵
        # print(result)

        # 寻找最优匹配
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        logger.info(f'坐标：min_val={min_val}, max_val={max_val}, min_loc={min_loc}, max_loc={max_loc}')
        max_loc_x = max_loc[0]

        # 返回缺口坐标
        return max_loc_x * (width / tw), 0

    @staticmethod
    def dragSlide(frame: ChromiumFrame, offset_x: int, offset_y: int, drag_element_id: str):
        """
        拖动滑块
        :param frame: 验证码iframe
        :param offset_x: 拖动距离X方向
        :param offset_y: 拖动距离Y方向
        :param drag_element_id: 拖动滑块的元素ID
        :return:
        """
        try:
            drag_element = frame(drag_element_id)
            if drag_element is None:
                logger.info(f"找不到指定元素, drag_element_id={drag_element_id}")
            else:
                logger.info(f'开始拖动滑块，offsetX={offset_x}, offsetY={offset_y}')
                drag_element.drag(offset_x, offset_y, 0.5)
        except Exception as e:
            logger.info(f"拖动滑块出错: {e}")

    @staticmethod
    def extract_filename_from_url(url):
        """
        从指定的 URL 中提取文件名。

        参数:
        url (str): 输入的 URL，例如 https://p9-catpcha.byteimg.com/tos-cn-i-188rlo5p4y/6a89ac0f574a43ce8f24167f242bb15e~tplv-188rlo5p4y-1.png

        返回:
        str: 提取的文件名，例如 6a89ac0f574a43ce8f24167f242bb15e~tplv-188rlo5p4y-1.png
        """
        # 使用 urlparse 解析 URL
        parsed_url = urlparse(url)

        # 提取路径部分并分割路径，获取最后一部分即文件名
        filename = parsed_url.path.split('/')[-1]

        return filename

    @staticmethod
    def assemble_full_path(directory: str, filename: str) -> str:
        """
        组装完整的文件路径。

        参数:
        directory (str): 目录路径，例如 "/path/to/directory"
        filename (str): 文件名，例如 "file.txt"

        返回:
        str: 组装好的完整路径，例如 "/path/to/directory/file.txt"
        """
        # 使用 os.path.join 拼接目录路径和文件名
        full_path = os.path.join(directory, filename)

        return full_path
