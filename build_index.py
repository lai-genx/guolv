"""
兼容 README 的知识库索引命令入口。

实际实现位于 scripts/build_index.py。本文件保留根目录命令：
    python build_index.py --reset
    python build_index.py --show
"""
from runpy import run_path
from pathlib import Path


if __name__ == "__main__":
    run_path(str(Path(__file__).parent / "scripts" / "build_index.py"), run_name="__main__")
