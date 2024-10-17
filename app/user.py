import time
import traceback

from DrissionPage._elements.none_element import NoneElement
from DrissionPage._pages.web_page import WebPage

from app import logging_config
from app.chrome import Chrome
from app.config import Config
from validator import Validator
logger = logging_config.get_logger(__name__)

config = Config()

class User:
    """
    @author: lisanlai
    """

    @staticmethod
    def autoLogin(_page: WebPage, username: str, password: str):
        """
        自动登录招商团长控制台
        :param _page: 页面对象
        :param username: 招商团长登录用户名
        :param password: 招商团长登录密码
        :return: MixPage
        """
        try:
            role_select_page = config.get('page', 'role_select_page')
            _page.get(role_select_page)
            # 进入招商团长登录页面
            zs_role = _page.ele(locator='text:招商团长', timeout=5)
            if isinstance(zs_role, NoneElement):
                logger.warning(f'没有找到招商团长角色按钮')
                return None
            zs_role.click.left(by_js=True)
            logger.info(f'选择招商团长登录角色')
            time.sleep(0.5)

            # 切换到邮箱登录
            email_login_btn = _page.ele('text:邮箱登录', timeout=5)
            if isinstance(email_login_btn, NoneElement):
                logger.warning(f'没有找到邮箱登录按钮')
                raise RuntimeError('没有找到邮箱登录按钮')
            email_login_btn.click.left(by_js=True)
            _page.wait.ele_displayed('tag:button@text()=登录')
            # time.sleep(1)
            # 填写登录用户名和密码
            username_input = _page.ele('tag:input@name=email', timeout=5)
            password_input = _page.ele('tag:input@name=password', timeout=5)
            username_input.input(username)
            password_input.input(password)
            _page.ele('tag:input@type=checkbox').click.left(by_js=True)
            login_btn = _page.ele('tag:button@text()=登录', timeout=5)
            login_btn.click.left(by_js=True)

            # 判断有没有出现验证码弹窗
            auto_login_verify = config.get('validator', 'auto_login_verify')
            if auto_login_verify == "True":
                User.verifySlideCode(_page)
                time.sleep(1)
            return _page
        except Exception as e:
            if _page is not None:
                logger.info(f'浏览器因为异常而关闭')
                _page.close()
            raise e

    @staticmethod
    def verifySlideCode(page: WebPage):
        """
        自动验证滑块验证码

        :param page: 指定页面
        :return: true or false
        """
        logger.info(f'开始验证滑块验证码,当前页面={page.url}')
        slide_container = page.ele('#ecomLoginForm-slide-container', timeout=5)
        if slide_container:
            frame = slide_container.child(1)
            time.sleep(1)
            if frame is None:
                logger.info('不需要校验验证码')
            else:
                iframe = page.get_frame(1)
                logger.info(f'找到验证码区域，url={iframe.url}')
                bg_image_id = config.get('validator', 'bg_image_id')
                slide_image_id = config.get('validator', 'slide_image_id')

                result = Validator.validate(iframe, bg_image_id, slide_image_id)
                if result:
                    logger.info(f'验证码校验成功')
                    time.sleep(0.5)
                    target_account = config.get('login', 'target_account')
                    target_account_btn = page.ele(f'text:{target_account}', timeout=5)
                    target_account_btn.click.left(by_js=True)
        else:
            logger.info('没找到验证码区域')

    @staticmethod
    def logout(exclude: str, force=False):
        """
        如果当前登录的用户不是exclude，那么自动logout
        :param exclude: logout排除在外的用户
        :param force: 强制logout
        :return:
        """
        _page = None
        try:
            _page = Chrome.createPage(no_img=True)
            touch_page = config.get('page', 'activity_page')
            _page.get(touch_page)
            logger.info(f'url={_page.url}')
            if _page.url == touch_page:
                logger.info(f'已经是登录态，准备logout')
                title_el = _page.ele("tag:span@class=btn-item-role-exchange-name__title", timeout=5)
                if isinstance(title_el, NoneElement):
                    logger.warn('没有找到团长名称元素')
                    return None
                title_el.hover()
                title = title_el.text
                logger.info(f'当前登录用户={title}')
                if force or title != exclude:
                    logger.info(f'退出当前登录')
                    _page.ele("text:退出").click.left(by_js=True)
                    time.sleep(0.5)
                    _page.ele("@text()=确定").click.left(by_js=True)
                    time.sleep(0.5)
            else:
                logger.info('当前不是登录状态')
        except Exception as e:
            logger.info("Stack Trace:", traceback.format_exc())
        finally:
            if _page is not None:
                _page.close()
