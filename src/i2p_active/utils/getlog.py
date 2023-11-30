import logging
import logging.handlers
import os

# 配置日志基本设置
def setup_logging(filename = "defult.log"):
    # 创建一个logger
    logger = logging.getLogger(filename.split(".")[0])
    logger.setLevel(logging.DEBUG)  # 可以根据需要设置不同的日志级别

    # 创建一个handler，用于写入日志文件
    log_dir = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
    log_dir = os.path.join("/" + log_dir, "logs")
    log_file = os.path.join(log_dir, filename)
    
    # 用于写入日志文件，当文件大小超过500MB时进行滚动
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=500*1024*1024, backupCount=3)
    file_handler.setLevel(logging.DEBUG)

    # 创建一个handler，用于将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 定义handler的输出格式
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger



#############################################
## use example 
# # 获取配置好的logger
# logger = getlog.setup_logging(file_name)

# # 记录日志
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
#############################################