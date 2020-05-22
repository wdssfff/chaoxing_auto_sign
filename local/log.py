import logging


def log_error_msg(func):
    def warp():
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.DEBUG)
        handler = logging.FileHandler('logs.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        try:
            data = func()
            logger.info(data)
            return data
        except Exception as e:
            logger.exception(e)
            return '程序出错,错误信息已记录日志'
    return warp

