import os
import configparser

from app import logging_config

logger = logging_config.get_logger(__name__)


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        port = os.environ.get('PORT') or self.get('default', 'port')
        # 检查端口号是否为 None 并进行转换
        if port is not None:
            self.PORT = int(port)
        else:
            raise ValueError("Port number is not specified in environment variables or config file")

        # database setting
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or self.get('database', 'url')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # scheduler setting
        self.SCHEDULER_API_ENABLED = True
        # 配置时区
        self.SCHEDULER_TIMEZONE = 'Asia/Shanghai'

    def get(self, section, option, fallback=None):
        return os.environ.get(f'{section}_{option}'.upper()) or self.config.get(section, option, fallback=fallback)
