"""
1)要求将所有级别的所有日志都写入磁盘文件中
2)all.log文件中记录所有的日志信息,日志格式为：日期和时间 - 日志级别 - 日志信息
3)error.log文件中单独记录error及以上级别的日志信息,日志格式为:日期和时间 - 日志级别 - 文件名[:行号] - 日志信息
4)要求all.log在每天凌晨进行日志切割
"""
import sys
import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

# 日期格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %p"
LOG_DIR = Path(sys.argv[0]).absolute().parent.parent / 'logs'

# 添加日志器的名称标识
logger = logging.getLogger('global_logger')
logger.setLevel(logging.DEBUG)

all_handler = TimedRotatingFileHandler(
    filename=LOG_DIR / 'all.log',
    when='midnight',
    interval=1,
    backupCount=7,
)
all_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

err_handler = logging.FileHandler(LOG_DIR / 'error.log')
err_handler.setLevel(logging.ERROR)
# 格式器
err_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d -%(pathname)s \n%(message)s")
)

# 给logger 添加处理器
logger.addHandler(all_handler)
logger.addHandler(err_handler)
