import sys
from pathlib import Path

BASE_DIR = str(Path(sys.argv[0]).absolute().parent.parent)
sys.path.append(BASE_DIR)
JWT_EXPIRY_SECOND = 30 * 60
SECRET_KEY = "vpZE98NR9G6XSvMOSmZUwzbyOAlEXA2QG+Sio0AM3x9dawEcKt82bLN9/aCNY4Hv"
USERS = [
    {"user_id": "1001", "user_name": "张三"},
    {"user_id": "1002", "user_name": "李四"},
    {"user_id": "1003", "user_name": "王五"},
]
INSTALLED_APPS = [
    'apis.shop'
]
DATABASES = {
    'shop': {
        'HOST': 'localhost',
        'PORT': 27017,
        'NAME': 'shop',
    },
}
