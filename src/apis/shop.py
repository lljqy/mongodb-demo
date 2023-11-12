from flask_graphql import GraphQLView

from src.schemas.shop import shop_schema

shop_graphql_view = GraphQLView.as_view('shop_graphql', schema=shop_schema, graphiql=True)
