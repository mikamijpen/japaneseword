import logging
import os
from logging.handlers import RotatingFileHandler
from utils import resource_path

def setup_logger():
    """设置日志记录器"""
    # 确保日志目录存在
    log_dir = resource_path("logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "app.log")
    
    # 创建一个日志记录器
    logger = logging.getLogger("JapaneseWordAppLogger")
    logger.setLevel(logging.ERROR)
    
    # 创建一个循环文件处理器
    handler = RotatingFileHandler(
        log_file, 
        maxBytes=1024*1024,  # 1 MB
        backupCount=5, 
        encoding='utf-8'
    )
    handler.setLevel(logging.ERROR)
    
    # 创建一个日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # 如果记录器没有处理器，则添加处理器
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

# 全局日志记录器实例
logger = setup_logger() 