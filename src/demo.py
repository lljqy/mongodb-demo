import sys
from pathlib import Path
from pprint import pprint

import requests

# 将当前根目录加载到python解释器的搜索路径
sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))

from src.evironment import init_settngs_module_path, get_settings

DEBUG = False
init_settngs_module_path(DEBUG)
settings = get_settings()

from src.apis.token_handler import TokenHandler

token = TokenHandler.generate_tokens(user_id='1002')

cookies = {
    'Pycharm-8eca8af5': '45e16931-75a9-4868-a4ac-229513271d04',
    'isg': 'BKSkE8UJnRGIkOld3OyujnI3daKWPcinEm9SQL7FMG8yaUQz5k2YN9oILcHxsQD_',
}
headers = {
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:5001',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
                  'Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sign': token
}
query_string = """
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
json_data = {
    'query': query_string,
    'variables': None,
}
response = requests.post(
    'http://localhost:5001/shop_graphql',
    cookies=cookies,
    headers=headers,
    json=json_data
)
pprint(response.json())
