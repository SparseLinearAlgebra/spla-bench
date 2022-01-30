import subprocess

import config

from lib.tool import ToolName


GRAPHBLAST_PATHS = config.TOOL_CONFIG[ToolName.graphblast]


def build():
    subprocess.check_call(
        [
            "make", "-B", f"--directory={GRAPHBLAST_PATHS.sources}", f"-j{config.BUILD.jobs}"
        ]
    )
