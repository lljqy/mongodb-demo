import os
import sys
from pathlib import Path
from importlib import import_module

# 将当前根目录加载到python解释器的搜索路径
sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))


def init_settngs_module_path(debug: bool = True) -> None:
    module_name = "src.settings.dev" if debug else "src.settings.prod"
    os.environ.setdefault("SETTINGS_MODULES", module_name)


def get_settings() -> object():
    return import_module(os.environ.get("SETTINGS_MODULES", "src.settings.dev"))
