from config import TOOL_CONFIG
from typing import Callable, List, Tuple
from pathlib import Path

import build.suitesparse as suitesparse

from build.graphblast import build as build_graphblast
from build.gunrock import build as build_gunrock
from build.lagraph import build as build_lagraph
from build.spla import build as build_spla
from lib.tool import ToolName
from lib.util import check_paths_exist


TOOL_BUILDERS = {
    ToolName.graphblast: build_graphblast,
    ToolName.gunrock: build_gunrock,
    ToolName.lagraph: build_lagraph,
    ToolName.spla: build_spla
}


def rebuild(builder: Callable[[], None], targets: List[Path]):
    builder()
    if not check_paths_exist(targets):
        not_built = '\n\t' + \
            '\n\t'.join(filter(lambda t: not t.exists(), targets))
        raise Exception(f'Not all targets were built:{not_built}')


def build(builder: Callable[[], None], targets: List[Path]):
    if check_paths_exist(targets):
        return
    rebuild(builder, targets)


def build_tool(tool: ToolName):
    build(TOOL_BUILDERS[tool], TOOL_CONFIG[tool].algo_exec_paths())


def rebuild_tool(tool: ToolName):
    rebuild(TOOL_BUILDERS[tool], TOOL_CONFIG[tool].algo_exec_paths())


def build_suitesparse() -> Tuple[Path, Path]:
    if check_paths_exist(suitesparse.chosen_method_targets()):
        return
    return suitesparse.do_chosen_method()


def rebuild_suitesparse() -> Tuple[Path, Path]:
    return suitesparse.do_chosen_method()
