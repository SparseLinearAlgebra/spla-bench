import os
import subprocess

from enum import Enum
from pathlib import Path
from typing import Tuple, List

import config
import lib.progress as progress

from lib.tool import ToolName
from lib.util import check_paths_exist, check_call


LAGRAPH_PATHS = config.TOOL_CONFIG[ToolName.lagraph]


def suitesparse_download() -> Tuple[Path, Path]:
    sp_info = config.SUITESPARSE.download
    output_directory: Path = sp_info.dest

    graphblas_include = output_directory / sp_info.include_rel
    graphblas_library = output_directory / sp_info.library_rel

    if not output_directory.exists():
        os.makedirs(output_directory)

    gb_archive_path = output_directory / 'archive'
    progress.download(sp_info.url, gb_archive_path)
    progress.unarchive(gb_archive_path, output_directory)
    os.remove(gb_archive_path)
    return graphblas_include, graphblas_library


def suitesparse_build() -> Tuple[Path, Path]:
    sp_info = config.SUITESPARSE.repo

    output_directory: Path = sp_info.dest

    if not output_directory.exists():
        os.makedirs(output_directory)

    gb_include = output_directory / sp_info.include_rel
    gb_build = output_directory / sp_info.build_rel
    gb_library = output_directory / sp_info.library_rel

    gb_cloned = check_paths_exist([gb_include])

    if not gb_cloned:
        print(f'Cloning GraphBLAS from {sp_info.url} to the {sp_info.dest}')
        check_call(
            [
                'git', 'clone', '--recursive',
                sp_info.url,
                output_directory
            ]
        )
    else:
        print(f'GraphBLAS is already cloned to the {output_directory}')

    print(f'Checking out branch {sp_info.branch}')
    check_call(
        [
            'git', 'checkout',
            sp_info.branch
        ],
        cwd=output_directory
    )

    print(f'Building GraphBLAS in the {gb_build}')

    env = config.make_build_env()

    check_call(
        [
            'cmake', '..'
        ],
        cwd=gb_build, env=env
    )

    check_call(
        [
            'make',
            config.jobs_flag()
        ],
        cwd=gb_build,
        env=env
    )

    return gb_include, gb_library


class SuitesparseMethod(Enum):
    local = 'local',
    build = 'build',
    download = 'downlod'

    def __str__(self):
        return self.value


def suitesparse_chosen_method() -> SuitesparseMethod:
    sp = config.SUITESPARSE

    gb_download = sp.download is not None
    gb_build = sp.repo is not None
    gb_use_local = sp.local is not None

    if sum([gb_download, gb_build, gb_use_local]) != 1:
        raise Exception(
            'Please choose exactly one option for SuiteSparse.GraphBLAS: download, build or use local version')

    if gb_use_local and not (sp.local.include and sp.local.library):
        raise Exception('Include or library for local SuiteSparse is not set')

    if gb_download:
        return SuitesparseMethod.download
    elif gb_build:
        return SuitesparseMethod.build
    return SuitesparseMethod.local


def suitesparse_do_chosen_method() -> Tuple[Path, Path]:
    sp = config.SUITESPARSE
    method = suitesparse_chosen_method()

    if method == SuitesparseMethod.local:
        return sp.local.include, sp.local.library
    elif method == SuitesparseMethod.download:
        return suitesparse_download()
    elif method == SuitesparseMethod.build:
        return suitesparse_build()

    raise Exception(f'Unknown SuiteSparse build method: {str(method)}')


def chosen_method_targets() -> List[Path]:
    sp = config.SUITESPARSE
    method = suitesparse_chosen_method()

    if method == SuitesparseMethod.local:
        return [
            sp.local.include,
            sp.local.library
        ]
    elif method == SuitesparseMethod.download:
        dest: Path = sp.download.dest
        return [
            dest / sp.download.include_rel,
            dest / sp.download.library_rel
        ]
    elif method == SuitesparseMethod.build:
        dest: Path = sp.repo.dest
        return [
            dest / sp.repo.include_rel,
            dest / sp.repo.library_rel
        ]

    raise Exception(f'Unknown SuiteSparse build method: {str(method)}')



def build():
    graphblas_include, graphblas_library = suitesparse_build()

    graphblas_include = graphblas_include.absolute()
    graphblas_library = graphblas_library.absolute()

    lagraph_root = LAGRAPH_PATHS.sources.absolute()
    lagraph_build_dir = lagraph_root / f'build_{str(suitesparse_chosen_method())}'

    if not os.path.exists(lagraph_build_dir):
        os.makedirs(lagraph_build_dir)

    env = config.make_build_env()
    env['GRAPHBLAS_INCLUDE_DIR'] = graphblas_include
    env['GRAPHBLAS_LIBRARY'] = graphblas_library

    check_call(
        [
            'cmake', '..',
            f'-DGRAPHBLAS_INCLUDE_DIR={graphblas_include}',
            f'-DGRAPHBLAS_LIBRARY={graphblas_library}'
        ],
        cwd=lagraph_build_dir,
        env=env
    )

    check_call(
        [
            'make',
            config.jobs_flag()
        ],
        cwd=lagraph_build_dir
    )

    os.symlink(LAGRAPH_PATHS.build, lagraph_build_dir)
