import logging
import logging.config

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'filename': 'app.log',
            'mode': 'a',
        },
    },
    'root': {  # 根日志记录器
        # 'handlers': ['console', 'file'],
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# 应用日志配置
logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name=None):
    """
    获取日志记录器。如果未提供名称，则返回根日志记录器。
    """
    return logging.getLogger(name)
