from typing import Dict
from datetime import datetime, timedelta

import jwt
from jwt import PyJWKError
from flask import current_app
from requests.status_codes import codes

from src.manage import get_settings

settings = get_settings()


class TokenHandler:
    USERS = getattr(settings, 'USERS')
    SECRET_KEY = getattr(settings, 'SECRET_KEY')
    JWT_EXPIRY_SECOND = getattr(settings, 'JWT_EXPIRY_SECOND')

    _algorithm = 'HS256'

    @classmethod
    def generate_tokens(cls, user_id: str) -> str:
        payload = {
            'user_id': user_id,
            'end_time': (datetime.now() + timedelta(seconds=cls.JWT_EXPIRY_SECOND)).timestamp(),
        }
        return jwt.encode(payload=payload, key=cls.SECRET_KEY, algorithm=cls._algorithm)

    @classmethod
    def verify_tokens(cls, token: str) -> Dict[str, str]:
        user_id, code, msg = 'user_id', 'code', 'message'
        try:
            data = jwt.decode(token, key=cls.SECRET_KEY, algorithms=cls._algorithm)
            current_app.logger.info(data)
            user = list(
                filter(
                    lambda u: u.get(user_id, '') == data.get(user_id) and
                              data.get('end_time') >= datetime.now().timestamp(),
                    cls.USERS
                )
            )
            if user:
                return {code: codes.ok, user_id: user[0].get(user_id)}
            else:
                return {code: codes.not_found, msg: '当前角色不存在, 或者用户身份验证过期'}
        except PyJWKError as e:
            current_app.logger.info(e)
        return {code: codes.internal_server_error, msg: "token验证失败"}
