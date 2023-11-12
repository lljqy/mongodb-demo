import sys
from pathlib import Path

# 将当前根目录加载到python解释器的搜索路径
sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))

from src.evironment import init_settngs_module_path, get_settings

DEBUG = False
init_settngs_module_path(DEBUG)
settings = get_settings()

from apis import mount

# 加载配置和路由信息
app = mount()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
