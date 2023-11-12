import sys
import warnings
from pathlib import Path
from typing import List, Dict
from abc import ABCMeta, abstractmethod
from string import punctuation, whitespace

import pandas as pd

from src.database.utils import MongoUtil
from src.models.shop import Categories, Products


class DFCleaner:
    EMPTY_STRING = ''
    _EXCLUDE_CHARS = ''.join((punctuation, whitespace))

    @staticmethod
    def clean_float(df: pd.DataFrame, float_columns: List[str]) -> pd.DataFrame:
        def _is_float(s: str) -> bool:
            try:
                float(s)
                return True
            except ValueError as _:
                return False

        for float_column in float_columns:
            df = df.loc[df[float_column].astype(str).apply(lambda x: _is_float(x)), :]
            df[float_column] = df[float_column].astype(float)
        return df

    @staticmethod
    def clean_integer(df: pd.DataFrame, integer_columns: List[str]) -> pd.DataFrame:
        for integer_column in integer_columns:
            df = df.loc[df[integer_column].astype(str).str.isdigit(), :]
            df[integer_column] = df[integer_column].astype(int)
        return df

    @classmethod
    def clean_string(cls, df: pd.DataFrame, string_columns: List[str]) -> pd.DataFrame:
        for string_column in string_columns:
            df[string_column] = df[string_column].fillna(cls.EMPTY_STRING)
            df[string_column] = df[string_column].astype(str).str.strip(cls._EXCLUDE_CHARS)
        return df


class Processor(metaclass=ABCMeta):
    _DATA_PATH = Path(sys.argv[0]).absolute().parent.parent / 'data'

    def __init__(self, using: str = 'default') -> None:
        self._mongo_util = MongoUtil(using)

    @staticmethod
    def _perform_common_transform(df_to_be_transform: pd.DataFrame, columns_relation: Dict[str, str]) -> pd.DataFrame:
        """
        对数据进行初步的清洗
        :param df_to_be_transform:
        :param columns_relation:
        :return: 清洗的结果
        """
        for column, data_type in columns_relation.items():
            method_name = f"clean_{data_type}"
            if not hasattr(DFCleaner, method_name):
                warnings.warn(f"无法清洗{column}: {data_type}类型的数据")
                continue
            df_to_be_transform = getattr(DFCleaner, method_name, lambda x, _: x)(df_to_be_transform, [column])
        return df_to_be_transform

    def _create_index(self, columns: List[str], collection_name: str, database='admin') -> None:
        self._mongo_util.create_index(columns, collection_name, database)

    @abstractmethod
    def _extract(self, chunk_size: int = 10, *args, **kwargs) -> None:
        raise NotImplementedError("必须在子类中实现`_extract`方法")

    @abstractmethod
    def _transform(self, df_chunks: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError("必须在子类中实现`_transformer`方法")

    @abstractmethod
    def _load(self, *args, **kwargs) -> None:
        raise NotImplementedError("必须在子类中实现`_load`方法")

    @abstractmethod
    def process(self, *args, **kwargs) -> None:
        raise NotImplementedError("必须在子类中实现`process`方法")


class ProductsProcessor(Processor):
    _database = Categories.get_db().name
    _products_columns_relation = {
        'product_id': 'integer',
        'name': 'string',
        'description': 'string',
        'price': 'float',
        'category_id': 'integer',
    }

    def _extract(self, chunk_size: int = 10000, *args, **kwargs) -> None:
        self._df_products_chunks = pd.read_csv(str(self._DATA_PATH / 'products.csv'), chunksize=chunk_size)

    def _transform(self, df_products_chunk: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df_products_chunk = self._perform_common_transform(df_products_chunk, self._products_columns_relation)
        df_products_chunk = df_products_chunk[
            (df_products_chunk.product_id != DFCleaner.EMPTY_STRING) &
            (df_products_chunk.category_id != DFCleaner.EMPTY_STRING) &
            (~df_products_chunk.price.isnull())]
        return df_products_chunk

    def _load(self, df_products_chunk: pd.DataFrame, collection_name: str, database: str) -> None:
        # todo: 此处模拟消息队列，做了一个重试的动作，后续可以将入库操作改为向消息队列发送写入请求保证数据不丢
        self._mongo_util.save(df_products_chunk, collection_name, database=database)

    def process(self, chunk_size: int = 1000) -> None:
        self._extract(chunk_size=chunk_size)
        collection_name = Products.get_collection().name
        if chunk_size:
            for df_products_chunk in self._df_products_chunks:
                df_products_chunk = self._transform(df_products_chunk)
                self._load(df_products_chunk, collection_name, database=self._database)
        else:
            self._load(self._df_products_chunks, collection_name, database=self._database)
        for index_name in ('category_id', 'price', 'name'):
            self._create_index([index_name], collection_name=collection_name, database=self._database)


class CategoriesProcessor(Processor):
    _database = Categories.get_db().name
    _categories_columns_relation = {'category_id': 'integer', 'category_name': 'string'}

    def _extract(self, chunk_size: int = 10, *args, **kwargs) -> None:
        self._df_categories_chunks = pd.read_csv(str(self._DATA_PATH / 'categories.csv'), chunksize=chunk_size)

    def _transform(self, df_categories_chunk: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df_categories_chunk = self._perform_common_transform(df_categories_chunk, self._categories_columns_relation)
        # 删除category_id为空的数据
        df_categories_chunk = df_categories_chunk[df_categories_chunk.category_id != DFCleaner.EMPTY_STRING]
        return df_categories_chunk

    def _load(self, df_categories_chunk: pd.DataFrame, collection_name: str, database: str) -> None:
        # todo: 此处模拟消息队列，做了一个重试的动作，后续可以将入库操作改为向消息队列发送写入请求保证数据不丢
        self._mongo_util.save(df_categories_chunk, collection_name, database=database)

    def process(self, chunk_size: int = 1000) -> None:
        self._extract(chunk_size=chunk_size)
        collection_name = Categories.get_collection().name
        if chunk_size:
            for df_categories_chunk in self._df_categories_chunks:
                df_categories_chunk = self._transform(df_categories_chunk)
                self._load(df_categories_chunk, collection_name, database=self._database)
        else:
            self._load(self._df_categories_chunks, collection_name, database=self._database)
        self._create_index(['category_name', 'category_id'], collection_name=collection_name, database=self._database)
