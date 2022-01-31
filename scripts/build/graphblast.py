import subprocess

import config
import lib.util as util

from lib.tool import ToolName


GRAPHBLAST_PATHS = config.TOOL_CONFIG[ToolName.graphblast]


def build():
    util.check_call(
        [
            "make", "-B", f"--directory={GRAPHBLAST_PATHS.sources}", f"-j{config.BUILD.jobs}"
        ]
    )
