#!/usr/bin/env python3

from distutils.command import check
from gettext import install
import sys
import os
import argparse
from types import TracebackType
import urllib.request
import tarfile
import subprocess
import traceback

from typing import List, Dict, Tuple

import shared

DEFAULT_GRB_VERSION = '6.1.4'
DEFAULT_CONDA_GRB_PACKAGE_HASH = {
    'macos': 'h4a89273',
    'windows': 'h0e60522',
    'linux': 'h9c3ff4c'
}[shared.SYSTEM]
CONDA_PLATFORM = {
    'macos': 'osx-64',
    'windows': 'win-64',
    'linux': 'linux-64'
}[shared.SYSTEM]
LAGRAPH_TARGETS = [
    'bfs_demo' + shared.EXECUTABLE_EXT,
    'tc_demo' + shared.EXECUTABLE_EXT,
    'sssp_demo' + shared.EXECUTABLE_EXT
]
SUITESPARSE_GITHUB = 'https://github.com/DrTimothyAldenDavis/GraphBLAS'
SUITESPRSE_BRANCH = 'v6.1.4'


def check_paths_exist(paths: List[str]) -> bool:
    return sum(map(lambda p: not os.path.exists(p), paths)) == 0


def build_graphblas(output_directory: str, env_vars: Dict[str, str], jobs: int, force_rebuild: bool) -> Tuple[str, str]:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    gb_include = os.path.join(output_directory, 'include')
    gb_build = os.path.join(output_directory, 'build')
    gb_library = os.path.join(gb_build, 'libgraphblas' + shared.TARGET_SUFFIX)

    already_built = check_paths_exist([gb_include, gb_library])

    if already_built and not force_rebuild:
        print(
            f'GraphBLAS already built: include: `{gb_include}`, library: `{gb_library}`')
        return gb_include, gb_library

    gb_cloned = check_paths_exist([gb_include])

    if not gb_cloned:
        print(
            f'Cloning GraphBLAS from {SUITESPARSE_GITHUB} to the {output_directory}')
        subprocess.check_call(
            ['git', 'clone', '--recursive', SUITESPARSE_GITHUB, output_directory])
        subprocess.check_call(
            ['git', 'checkout', SUITESPRSE_BRANCH]
        )
    else:
        print(f'GraphBLAS is already cloned to the {output_directory}')

    print(f'Building GraphBLAS in the {gb_build}')

    env = os.environ.copy()
    for env_var, env_value in env_vars.items():
        env[env_var] = env_value

    subprocess.check_call(['cmake', '..'], cwd=gb_build, env=env)
    make_jobs_arg = []
    if jobs != 0:
        make_jobs_arg.append(f'-j{jobs}')

    subprocess.check_call(['make'] + make_jobs_arg, cwd=gb_build, env=env)

    if not check_paths_exist([gb_library]):
        raise Exception(f'GraphBLAS library was not found in the {gb_library}')

    print(f'Successfully built GraphBLAS: {gb_library}')

    return gb_include, gb_library


def install_graphblas(grb_url: str, output_directory: str, ignore_cached: bool) -> Tuple[str, str]:
    graphblas_include = os.path(output_directory) / 'include'
    graphblas_library = os.path(output_directory) / \
        'lib' / 'libgraphblas' + shared.TARGET_SUFFIX

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    elif not ignore_cached:
        if check_paths_exist([graphblas_include, graphblas_library]):
            print(f'GraphBLAS is already installed in the {output_directory}')
            return graphblas_include, graphblas_library

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    grb_download_req = urllib.request.Request(grb_url, headers=headers)
    gb_archive_path = os.path.join(output_directory, 'archive')
    print(f'Downloading graphblas: {grb_url}')
    with urllib.request.urlopen(grb_download_req) as graphblas_tar:
        content = graphblas_tar.read()
        with open(gb_archive_path, 'wb') as dest_file:
            dest_file.write(content)
            print(f'Graphblas archive is downloaded: {gb_archive_path}')
    with tarfile.open(gb_archive_path, 'r:bz2') as gb_unarchived:
        gb_unarchived.extractall(output_directory)
        print(f'Graphblas is unarchived: {output_directory}')
    os.remove(gb_archive_path)
    check_paths_exist([graphblas_include, graphblas_library])
    return graphblas_include, graphblas_library


def build_lagraph(graphblas_include: str, graphblas_library: str, lagraph_root: str, env_vars: Dict[str, str], jobs: int, force_rebuild: bool) -> None:
    graphblas_include = os.path.abspath(graphblas_include)
    graphblas_library = os.path.abspath(graphblas_library)
    lagraph_root = os.path.abspath(lagraph_root)

    config = {
        'GraphBLAS include: ': graphblas_include,
        'GraphBLAS library: ': graphblas_library,
        'LaGraph root:      ': lagraph_root
    }

    print(f'Building LaGraph with configuration: {config}')

    lagraph_build_dir = os.path.join(lagraph_root, 'build')

    targets_dir = os.path.join(lagraph_build_dir, 'src', 'benchmark')
    targets_paths = list(
        map(lambda t: os.path.join(targets_dir, t), LAGRAPH_TARGETS))

    all_targets_str = '\t' + '\n\t'.join(targets_paths)

    if not force_rebuild and check_paths_exist(targets_paths):
        print(f'All targets are already built:\n{all_targets_str}')
        return

    if not os.path.exists(lagraph_build_dir):
        os.makedirs(lagraph_build_dir)

    env_vars['GRAPHBLAS_INCLUDE_DIR'] = graphblas_include
    env_vars['GRAPHBLAS_LIBRARY'] = graphblas_library

    env = os.environ.copy()
    for env_var, env_value in env_vars.items():
        env[env_var] = env_value

    subprocess.check_call(['cmake', '..', f'-DGRAPHBLAS_INCLUDE_DIR={graphblas_include}', f'-DGRAPHBLAS_LIBRARY={graphblas_library}'],
                          cwd=lagraph_build_dir,
                          env=env)

    make_jobs_arg = []
    if jobs != 0:
        make_jobs_arg.append(f'-j{jobs}')

    subprocess.check_call(['make'] + make_jobs_arg, cwd=lagraph_build_dir)

    if not check_paths_exist(targets_paths):
        raise Exception(
            f'All of the following targets were expected to build, but some did not: {all_targets_str}')

    print(f'Successfully built LaGraph:\n{all_targets_str}')


def clear_empty_vals(d: Dict) -> Dict:
    return dict(filter(lambda i: i[1] is not None, d.items()))


def main(args: List[str]) -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--j',
                        default=8,
                        help='Number of threads used to build (set to 0 to remove this flag)',
                        dest='jobs')
    parser.add_argument('--cc',
                        default=None,
                        help='Path to CC compiler (automatically detected by cmake by default)')
    parser.add_argument('--cxx',
                        default=None,
                        help='Path to CXX compiler (automatically detected by cmake by default)')
    parser.add_argument('--gb_build',
                        default=None,
                        help='Clone GraphBLAS to the `gb_build` and use this version to build LaGraph')
    parser.add_argument('--gb_download',
                        default=None,
                        help='GraphBLAS.SuiteSparse download dir. Set if you want to use precompiled version. Or set `gb_include` `gb_library`')
    parser.add_argument('--gb_include',
                        default=None,
                        help='Path to the GraphBLAS headers')
    parser.add_argument('--gb_library',
                        default=None,
                        help='Path to the GraphBLAS library: libgraphblas.(so|dylib|dll)')
    parser.add_argument('--lg',
                        default=os.path.join(shared.DEPS, 'lagraph'),
                        help='LaGraph source directory')
    parser.add_argument('--grb_url',
                        default=f'https://anaconda.org/conda-forge/graphblas/{DEFAULT_GRB_VERSION}/download/{CONDA_PLATFORM}/graphblas-{DEFAULT_GRB_VERSION}-{DEFAULT_CONDA_GRB_PACKAGE_HASH}_0.tar.bz2',
                        help='Version of GraphBLAS to download')
    parser.add_argument('--ignore_cached_grb',
                        action='store_true',
                        help='Ignore downloaded binaries of GraphBLAST int the `gb_download`')
    parser.add_argument('--force_rebuild_lg',
                        action='store_true',
                        help='Rebuild LaGraph')
    parser.add_argument('--force_rebuild_gb',
                        action='store_true',
                        help='Rebuild GraphBLAS')
    args = parser.parse_args()

    if args.jobs < 0:
        raise Exception('`jobs` must be non-negative')

    gb_download = args.gb_download is not None
    gb_build = args.gb_build is not None
    gb_use_local = args.gb_include is not None

    if sum([gb_download, gb_build, gb_use_local]) != 1:
        raise Exception(
            'Please choose exactly one option for GraphBLAS: download, build or use local version')

    if gb_use_local and not args.gb_library:
        raise Exception('Set `gb_library` to use local version of GraphBLAS')

    if not os.path.exists(args.lg):
        raise Exception(f'LaGraph path does not exist: {args.lg}')

    gb_include_path = args.gb_include
    gb_library_path = args.gb_library

    env_vars = clear_empty_vals({
        'CC': args.cc,
        'CXX': args.cxx
    })

    if gb_download:
        gb_include_path, gb_library_path = install_graphblas(args.grb_url,
                                                             args.gb_download,
                                                             args.ignore_cached_grb)
    if gb_build:
        gb_include_path, gb_library_path = build_graphblas(args.gb_build,
                                                           env_vars,
                                                           args.jobs,
                                                           args.force_rebuild_gb)
    build_lagraph(gb_include_path,
                  gb_library_path,
                  args.lg,
                  env_vars,
                  args.jobs,
                  args.force_rebuild_lg)


if __name__ == '__main__':
    main(sys.argv[1:])
    print('Done!')
