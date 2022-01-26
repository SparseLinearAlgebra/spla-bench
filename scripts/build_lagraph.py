#!/usr/bin/env python3

import sys
import os
import argparse
from types import TracebackType
import urllib.request
import tarfile
import subprocess
import traceback

from typing import List, Dict

import shared


DEFAULT_GRB_VERSION = '6.1.4'
DEFAULT_CONDA_GRB_PACKAGE_HASH = 'h9c3ff4c'
LAGRAPH_TARGETS = ['bfs_demo', 'tc_demo', 'sssp_demo']


def check_paths_exist(paths: List[str]) -> bool:
    return sum(map(lambda p: not os.path.exists(p), paths)) == 0


def install_graphbas(grb_url: str, output_directory: str, ignore_cached: bool) -> None:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    elif not ignore_cached:
        graphblas_include = f'{output_directory}/include'
        graphblas_library = f'{output_directory}/lib/libgraphblas.so'

        if check_paths_exist([graphblas_include, graphblas_library]):
            print(f'GraphBLAS is already installed in the {output_directory}')
            return

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


def build_lagraph(graphblas_root: str, lagraph_root: str, env_vars: Dict[str, str], jobs: int, force_rebuild: bool) -> None:
    graphblas_root = os.path.abspath(graphblas_root)
    lagraph_root = os.path.abspath(lagraph_root)

    graphblas_include = os.path.join(graphblas_root, 'include')
    graphblas_library = os.path.join(graphblas_root, 'lib', 'libgraphblas.so')
    lagraph_build_dir = os.path.join(lagraph_root, 'build')

    targets_dir = os.path.join(lagraph_build_dir, 'src', 'benchmark')
    targets_paths = list(map(lambda t: os.path.join(targets_dir, t), LAGRAPH_TARGETS))

    all_targets_str = '\t' + '\t\n'.join(targets_paths)

    if not force_rebuild and check_paths_exist(targets_paths):
        print(f'All targets are already built: {all_targets_str}')
        return

    if not os.path.exists(lagraph_build_dir):
        os.makedirs(lagraph_build_dir)

    env_vars['GRAPHBLAS_INCLUDE_DIR'] = graphblas_include
    env_vars['GRAPHBLAS_LIBRARY'] = graphblas_library

    env = os.environ.copy()
    for env_var, env_value in env_vars.items():
        env[env_var] = env_value

    subprocess.check_call(['cmake', '..', f'-DGRAPHBLAS_INCLUDE_DIR={graphblas_include}', f'-DGRAPHBLAS_LIBRARY={graphblas_library}'],
                          cwd=lagraph_build_dir)

    make_jobs_arg = []
    if jobs != 0:
        make_jobs_arg.append(f'-j{jobs}')

    subprocess.check_call(['make'] + make_jobs_arg, cwd=lagraph_build_dir)

    if not check_paths_exist(targets_paths):
        raise Exception(f'All of the following targets were expected to build, but some did not: {all_targets_str}')

    print(f'Successfully built LaGraph: {all_targets_str}')


def clear_empty_vals(d: Dict) -> Dict:
    return dict(filter(lambda i: i[1] is not None, d.items()))


def main(args: List[str]) -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--j',
                        default=8,
                        help='Number of threads used to build',
                        dest='jobs')
    parser.add_argument('--cc',
                        default=None,
                        help='Path to CC compiler (automatically detected by cmake by default)')
    parser.add_argument('--cxx',
                        default=None,
                        help='Path to CXX compiler (automatically detected by cmake by default)')
    parser.add_argument('--gb',
                        default=os.path.join(shared.DEPS, 'graphblast'),
                        help='GraphBLAS.SuiteSparse download dir')
    parser.add_argument('--lg',
                        default=os.path.jon(shared.DEPS, 'lagraph'),
                        help='LaGraph source directory')
    parser.add_argument('--grb_url',
                        default=f'https://anaconda.org/conda-forge/graphblas/{DEFAULT_GRB_VERSION}/download/linux-64/graphblas-{DEFAULT_GRB_VERSION}-{DEFAULT_CONDA_GRB_PACKAGE_HASH}_0.tar.bz2',
                        help='Version of GraphBLAS to install')
    parser.add_argument('--ignore_cached_grb',
                        action='store_true',
                        help='Ignore downloaded version of GraphBLAST int the \'gb\'')
    parser.add_argument('--force_rebuild_lg',
                        action='store_true',
                        help='Rebuild LaGraph')
    args = parser.parse_args()

    assert args.jobs >= 0

    if not os.path.exists(args.lg):
        raise Exception(f'Path does not exist: {args.lg}')

    install_graphbas(args.grb_url, args.gb, args.ignore_cached_grb)

    env = {
        'CC': args.cc,
        'CXX': args.cxx
    }

    build_lagraph(args.gb,
                  args.lg,
                  clear_empty_vals(env),
                  args.jobs,
                  args.force_rebuild_lg)


if __name__ == '__main__':
    main(sys.argv[1:])
    print('Done!')
