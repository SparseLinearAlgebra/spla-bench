import os

from typing import List, Union
from pathlib import Path


def print_status(x, status: str, *args):
    print(f'[{str(x)} | {status}]:', *args)

def check_paths_exist(paths: List[Union[str, Path]]) -> bool:
    return sum(map(lambda p: not os.path.exists(p), paths)) == 0

def parent_directory(path: Path) -> Path:
    parents = path.parents
    if len(parents) < 1:
        raise Exception(f'Path `{path}` does not have a parent')
    return parents[0]

def file_name(path: Path) -> str:
    return path.resolve().name
