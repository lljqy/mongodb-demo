import json
from typing import List as TypeList

import pandas as pd
from graphene_mongo import MongoengineObjectType
from graphene import ObjectType, List, Schema, String, Float, ResolveInfo

from src.models.shop import Categories, Products

# 任何查询接口最多返回450条信息进行检索
DATA_LIMIT = 450


class ProductsType(MongoengineObjectType):
    query_columns = ('name', 'description', 'price', 'category_id')

    class Meta:
        model = Products


class CategoriesType(MongoengineObjectType):
    query_columns = ('category_name', 'category_id')

    class Meta:
        model = Categories


class Query(ObjectType):
    products = List(ProductsType, name=String(), price_min=Float(), price_max=Float(), category_name=String())
    categories = List(CategoriesType, category_name=String(required=True))

    @staticmethod
    def resolve_products(_: str, __: ResolveInfo, **kwargs) -> TypeList[Products]:
        err_float = -1.0
        queryset = Products.objects().only(*ProductsType.query_columns)
        name = kwargs.pop('name', '').strip()
        if name:
            queryset = queryset.filter(name=name)
        category_name = kwargs.pop('category_name', '').strip()
        if category_name:
            categories_data = json.loads(
                Categories.objects(category_name=category_name).only(*CategoriesType.query_columns).to_json())
            if categories_data:
                df_categories = pd.DataFrame(categories_data).loc[:, CategoriesType.query_columns]
                categories_ids = df_categories['category_id'].unique().tolist()
            else:
                categories_ids = list()
            queryset = queryset.filter(category_id__in=categories_ids)
        price_min = kwargs.pop('price_min', err_float)
        if price_min > err_float:
            queryset = queryset.filter(price__gte=price_min)
        price_max = kwargs.pop('price_max', err_float)
        if price_max > err_float:
            queryset = queryset.filter(price__lte=price_max)
        return queryset.limit(DATA_LIMIT)

    @staticmethod
    def resolve_categories(_: str, __: ResolveInfo, **kwargs) -> TypeList[Categories]:
        category_name = kwargs.pop('category_name', '')
        queryset = Categories.objects().only(*CategoriesType.query_columns)
        if category_name:
            queryset = queryset.filter(category_name=category_name)
        return queryset.limit(DATA_LIMIT)


shop_schema = Schema(query=Query)

if __name__ == '__main__':
    query = """
        query {  
              products(categoryName: "izfxqabkfy") {  
                name  
                description  
                price,
                categoryId
              }
              categories(categoryName: "izfxqabkfy"){
                categoryName,
                categoryId
              }
            }
    """
    result = shop_schema.execute(query)
    print(result)
