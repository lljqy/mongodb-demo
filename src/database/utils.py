import time
from functools import wraps
from datetime import datetime
from typing import Callable, List

import pandas as pd
from pymongo import MongoClient, ASCENDING

from src.manage import settings
from src.log.log_handler import logger

DATABASES = getattr(settings, 'DATABASES')


def _time_print(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def retry(retry_times: int = 3) -> Callable:
    def inner(func: Callable) -> Callable:
        @wraps(func)
        def run(*args, **kwargs) -> None:
            total = left = retry_times
            while left > 0:
                try:
                    func(*args, **kwargs)
                    break
                except Exception as e:
                    logger.error(f"{func.__name__}执行出错, 原因是{e.args}, 参数是{args}, {kwargs}: {total + 1 - left}/{total}")
                    _time_print(f"{func.__name__}执行出错, 原因是{e.args}: {left}/{total}")
                    time.sleep(5)
                    left -= 1

        return run

    return inner


class MongoUtil:

    def __init__(self, using: str = "default") -> None:
        db_settings = DATABASES[using]
        # 连接到 MongoDB
        self._client = MongoClient(f"mongodb://{db_settings['HOST']}:{db_settings['PORT']}/")

    def __enter__(self) -> MongoClient:
        return self._client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
            下文方法：负责离开语句块的清理操作，释放链接资源
            exc_type：异常类型，如果执行无异常，值为None
            exc_val：异常值，如果执行无异常，值为None
            exc_tb：traceback信息，如果执行无异常，值为None
        """
        self._client.close()

    @retry(retry_times=3)
    def save(self, df: pd.DataFrame, collection_name: str, database='admin') -> None:
        if 'add_time' not in df.columns:
            df['add_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = self._client[database]
        collection = db[collection_name]
        collection.insert_many(df.to_dict('records'))

    def create_index(self, columns: List[str], collection_name: str, database='admin') -> None:
        db = self._client[database]
        collection = db[collection_name]
        if '_'.join([f"{col}_1" for col in columns]) in collection.index_information():
            return
        collection.create_index([(column, ASCENDING) for column in columns], background=True)
