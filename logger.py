import logging
import os
from datetime import datetime

def setup_logger():
    """设置日志系统"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建主日志记录器
    logger = logging.getLogger('verification_bot')
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出 - 按日期命名
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(
        f'logs/bot_{today}.log', 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 错误日志单独记录
    error_handler = logging.FileHandler(
        f'logs/errors_{today}.log', 
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name=None):
    """获取日志记录器"""
    if name:
        return logging.getLogger(f'verification_bot.{name}')
    return logging.getLogger('verification_bot')