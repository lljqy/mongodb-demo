from src.models.shop import Categories, Products
from src.etl.data_processor import ProductsProcessor, CategoriesProcessor


class ETLScheduler:

    def __init__(self) -> None:
        self._processors = {
            ProductsProcessor: Products.__connection_name__,
            CategoriesProcessor: Categories.__connection_name__,
        }

    def perform_etl(self, chunk_size: int = 10000) -> None:
        for processor_class, using in self._processors.items():
            processor_class(using).process(chunk_size=chunk_size)
