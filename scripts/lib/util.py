from asyncio import subprocess
import os
import subprocess

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


def check_call(args, *other_args, **kwargs):
    print_status('subprocess', 'check_call', *args)
    return subprocess.check_call(args, *other_args, **kwargs)


def check_output(args, *other_args, **kwargs):
    print_status('subprocess', 'check_output', *args)
    return subprocess.check_output(args, *other_args, **kwargs)
