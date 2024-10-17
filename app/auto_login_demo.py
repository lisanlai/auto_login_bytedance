import os
import time

from app import logging_config
from app.chrome import Chrome
from app.config import Config
from app.user import User

logger = logging_config.get_logger(__name__)
config = Config()

if __name__ == '__main__':

    page = Chrome.createPage(no_img=False)
    # 如果活动ID存在，就跳转到对应的活动页面
    role_select_page = config.get('page', 'role_select_page')
    logger.info(f'role_select_page={role_select_page}')
    page.get(role_select_page)
    time.sleep(1)
    if role_select_page == page.url:
        page.close()
        login_page = Chrome.createPage(no_img=False)
        # 自动登录
        username = os.environ.get('LOGIN_USERNAME') or config.get('login', 'username')
        password = os.environ.get('LOGIN_PASSWORD') or config.get('login', 'password')
        page = User.autoLogin(login_page, username, password)
        time.sleep(0.5)