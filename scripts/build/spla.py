import subprocess
import os

import config

from lib.tool import ToolName
from lib.util import check_call

SPLA_PATHS = config.TOOL_CONFIG[ToolName.spla]


def build():
    if not os.path.exists(SPLA_PATHS.build):
        os.makedirs(SPLA_PATHS.build)

    check_call(
        [
            'cmake',
            '-S', SPLA_PATHS.sources,
            '-B', SPLA_PATHS.build,
            '-DCMAKE_BUILD_TYPE=Release'
        ],
        env=config.make_build_env()
    )

    check_call(
        [
            "make", config.jobs_flag()
        ],
        cwd=SPLA_PATHS.build
    )
