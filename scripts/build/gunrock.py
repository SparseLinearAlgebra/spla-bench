import itertools
import subprocess

import config
import lib.util as util

from lib.tool import ToolName


GUNROCK_CONFIG = config.TOOL_CONFIG[ToolName.gunrock]


def build():
    env = config.make_build_env()

    autodetect = GUNROCK_CONFIG.config.autodetect
    gencode = GUNROCK_CONFIG.config.gencode

    autodetect_or_gencode = "-DCUDA_AUTODETECT_GENCODE=ON"

    if not autodetect:
        autodetect_or_gencode = f"-DGUNROCK_GENCODE_{str(gencode)}=ON"

    util.check_call(
        [
            "cmake", str(GUNROCK_CONFIG.sources),
            "-B", str(GUNROCK_CONFIG.build)
        ],
        env=env
    )

    util.check_call(
        [
            "cmake", "--build", str(GUNROCK_CONFIG.build),
            autodetect_or_gencode
        ] +
        list(itertools.chain(*[["-t", t] for t in GUNROCK_CONFIG.algo_exec_names()])) +
        ["-j", str(config.BUILD.jobs)]
    )
