from datetime import datetime

from mongoengine import connect, Document, StringField, IntField, FloatField, DateTimeField

from src.evironment import get_settings

settings = get_settings()
DATABASES = getattr(settings, 'DATABASES', dict())
_connection_name = "shop"

connect(
    alias="shop-alias",
    db=DATABASES[_connection_name]['NAME'],
    host=DATABASES[_connection_name]['HOST'],
    port=DATABASES[_connection_name]['PORT']
)


class MethodMixin:

    @classmethod
    def get_db(cls):
        return cls._get_db()

    @classmethod
    def get_meta_data(cls):
        return cls._meta

    @classmethod
    def get_collection(cls):
        return cls._get_collection()


class Categories(Document, MethodMixin):
    __connection_name__ = _connection_name
    meta = {
        'collection': 't_categories',
        'db_alias': 'shop-alias',
        'indexes': [('category_name', 'category_id')]
    }
    category_id = IntField(required=True)
    category_name = StringField(default='')
    add_time = DateTimeField(default=datetime.now())


class Products(Document, MethodMixin):
    __connection_name__ = _connection_name
    meta = {
        'collection': 't_products',
        'db_alias': 'shop-alias',
        'indexes': ['category_id', 'name', 'price']
    }
    product_id = IntField(required=True)
    name = StringField(default='')
    description = StringField(default='')
    price = FloatField(default=0.0)
    category_id = IntField()
    add_time = DateTimeField(default=datetime.now())
