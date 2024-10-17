import os

from DrissionPage._configs.chromium_options import ChromiumOptions
from DrissionPage._pages.web_page import WebPage

from app import logging_config
from app.config import Config
from app.util import Util
logger = logging_config.get_logger(__name__)

config = Config()

class Chrome:
    """
    @author: lisanlai
    """

    @staticmethod
    def createPage(no_img=False):
        """
         创建chrome页面
        :return: 页面对象
        """
        co = ChromiumOptions()
        user_agent = config.get('chromium_options', 'user_agent')
        co.set_user_agent(user_agent)
        address = config.get('chromium_options', 'address') or r'127.0.0.1:9222'
        co.set_address(address)
        co.no_imgs(on_off=no_img)
        co.set_argument('--no-default-browser-check')
        co.set_argument('--disable-suggestions-ui')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-first-run-ui')
        co.set_argument('--no-first-run')
        co.set_argument('--disable-infobars')
        co.set_argument('--disable-popup-blocking')
        co.set_argument('--hide-crash-restore-bubble')
        co.set_argument('--disable-features=PrivacySandboxSettings4')
        co.set_argument('--window-size=1920x1080')
        co.set_argument('--start-maximized')
        # 阻止“自动保存密码”的提示气泡
        co.set_pref('credentials_enable_service', False)
        # 阻止“要恢复页面吗？Chrome未正确关闭”的提示气泡
        co.set_argument('--hide-crash-restore-bubble')
        co.set_argument("--disable-gpu")
        co.set_argument("--disable-dev-shm-usage")
        co.set_argument("--disable-popup-blocking")
        co.set_argument("--mute-audio")
        co.set_load_mode('normal')
        if config.get('setting', 'env') == 'prod':
            browser_path = config.get('chromium_options', 'browser_path') or r'/opt/google/chrome/google-chrome'
            co.set_browser_path(browser_path)
        if Util.str_to_bool(config.get("chromium_options", "header_less")):
            co.headless(on_off=True)
        _page = WebPage(chromium_options=co)
        return _page
