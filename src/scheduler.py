import sys
from pathlib import Path

# 将当前根目录加载到python解释器的搜索路径
sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))
from src.evironment import init_settngs_module_path

DEBUG = False
init_settngs_module_path(DEBUG)

from src.etl.etl_scheculer import ETLScheduler

if __name__ == '__main__':
    etl_scheduler = ETLScheduler()
    etl_scheduler.perform_etl()
