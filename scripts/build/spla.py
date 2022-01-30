import subprocess
import os

import config

from lib.tool import ToolName

SPLA_PATHS = config.TOOL_CONFIG[ToolName.spla]


def build():
    if not os.path.exists(SPLA_PATHS.build):
        os.makedirs(SPLA_PATHS.build)

    subprocess.check_call(
        [
            "cmake", SPLA_PATHS.sources,
            "-DCMAKE_BUILD_TYPE=Release"
        ],
        cwd=SPLA_PATHS.build,
        env=config.make_build_env()
    )

    subprocess.check_call(
        [
            "make", config.jobs_flag()
        ],
        cwd=SPLA_PATHS.build
    )
