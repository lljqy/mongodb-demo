from typing import Optional

from requests.status_codes import codes
from flask import Flask, jsonify, request

from src.evironment import get_settings
from src.log.log_handler import all_handler
from src.apis.shop import shop_graphql_view

settings = get_settings()


def mount() -> Flask:
    app = Flask(__name__)
    # 配置密钥
    app.config.__setitem__('SECRET_KEY', getattr(settings, 'SECRET_KEY'))
    # 设置日志处理器
    app.logger.addHandler(all_handler)
    # 配置路由
    app.add_url_rule('/shop_graphql', view_func=shop_graphql_view)

    @app.before_request
    def before_request() -> Optional[jsonify]:
        code, sign = 'code', 'sign'
        if sign not in request.headers:
            return jsonify({code: codes.unauthorized, 'error': 'Unauthorized'})
        token = request.headers.get(sign, '')
        from src.apis.token_handler import TokenHandler
        validate_data = TokenHandler.verify_tokens(token)
        if validate_data.get(code) != codes.ok:
            return jsonify(validate_data)

    return app
