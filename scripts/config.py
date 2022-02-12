import platform
import os

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from types import SimpleNamespace as Namespace
from enum import Enum

import lib.util as util

from lib.tool import ToolName
from lib.algorithm import AlgorithmName

"""
System information
"""

SYSTEM = {'Darwin': 'macos', 'Linux': 'linux',
          'Windows': 'windows'}[platform.system()]
EXECUTABLE_EXT = {'macos': '', 'windows': '.exe', 'linux': ''}[SYSTEM]
TARGET_SUFFIX = {'macos': '.dylib', 'linux': '.so', 'windows': '.dll'}[SYSTEM]

"""
This repository paths
"""

# Path to the root directory of spla-bench project
ROOT = Path(__file__).parent.parent

# Path to the directory, where datasets will be downloaded
# [MUTABLE]
DATASET_FOLDER = ROOT / 'dataset'

# Path to the deps dataset
DEPS = ROOT / 'deps'


@dataclass
class ToolConfigurations:
    """
    Paths and other information about the third party tools
    """

    # Path to the sources of tool
    sources: Path

    # Path to the build directory of tool
    build: Path

    # Relative paths to the algorithm binaries (from the build directory)
    algo_rel: Dict[AlgorithmName, Path]

    # Other configurations of the tool
    config: Namespace

    def algo_exec_paths(self) -> List[Path]:
        paths = []
        for exec in self.algo_rel.values():
            paths.append(self.build / exec.with_suffix(EXECUTABLE_EXT))
        return paths

    def algo_exec_names(self) -> List[str]:
        names = []
        for exec in self.algo_rel.values():
            names.append(exec.name)
        return names

    def are_all_built(self) -> bool:
        return util.check_paths_exist(self.algo_exec_paths())


class SmArchitecture(Enum):
    SM10 = 'SM10'
    SM13 = 'SM13'
    SM20 = 'SM20'
    SM30 = 'SM30'
    SM35 = 'SM35'
    SM37 = 'SM37'
    SM50 = 'SM50'
    SM52 = 'SM52'
    SM60 = 'SM60'
    SM61 = 'SM61'
    SM70 = 'SM70'
    SM72 = 'SM72'
    SM75 = 'SM75'
    SM80 = 'SM80'

    def __str__(self):
        return self.value


TOOL_CONFIG: Dict[ToolName, ToolConfigurations] = {
    ToolName.lagraph: ToolConfigurations(
        sources=DEPS / 'lagraph',
        build=DEPS / 'lagraph' / 'build',
        algo_rel={
            AlgorithmName.bfs: Path('sources') / 'benchmark' / 'bfs_demo',
            AlgorithmName.sssp: Path('sources') / 'benchmark' / 'sssp_demo',
            AlgorithmName.tc: Path('sources') / 'benchmark' / 'tc_demo'
        },
        config=Namespace()
    ),

    ToolName.spla: ToolConfigurations(
        sources=DEPS / 'spla',
        build=DEPS / 'spla' / 'build',
        algo_rel={
            AlgorithmName.bfs: Path('spla_bfs'),
            AlgorithmName.sssp: Path('spla_sssp'),
            AlgorithmName.tc: Path('spla_tc')
        },
        config=Namespace()
    ),

    ToolName.graphblast: ToolConfigurations(
        sources=DEPS / 'graphblast',
        build=DEPS / 'graphblast' / 'bin',
        algo_rel={
            AlgorithmName.bfs: Path('gbfs'),
            AlgorithmName.sssp: Path('gsssp'),
            AlgorithmName.tc: Path('gtc')
        },
        config=Namespace(
            # 0: do not display per iteration timing, 1: display per iteration timing
            # [MUTABLE]
            timing=0,

            # False: run CPU verification, True: skip CPU algorithm verification
            # [MUTABLE]
            skip_cpu_verify=False
        )
    ),

    ToolName.gunrock: ToolConfigurations(
        sources=DEPS / 'gunrock',
        build=DEPS / 'gunrock' / 'build',
        algo_rel={
            AlgorithmName.bfs: Path('') / 'bin' / 'bfs',
            AlgorithmName.sssp: Path('') / 'bin' / 'sssp',
            AlgorithmName.tc: Path('') / 'bin' / 'gtc',
        },
        config=Namespace(
            # Autodetect target architecture
            # [MUTABLE]
            autodetect=True,

            # Target sm and compute architecture
            # [MUTABLE]
            gencode=SmArchitecture.SM61
        )
    )
}


def tool_algo_exec_path(name: ToolName, algo: AlgorithmName):
    return TOOL_CONFIG[name].build / TOOL_CONFIG[name].algo_rel[algo].with_suffix(EXECUTABLE_EXT)


"""
Conda repository with GraphBLAS build

[MUTABLE]

"""
CONDA_GRB_REPO = Namespace(
    hash={
        'macos': 'h4a89273',
        'windows': 'h0e60522',
        'linux': 'h9c3ff4c'
    }[SYSTEM],

    platform={
        'macos': 'osx-64',
        'windows': 'win-64',
        'linux': 'linux-64'
    }[SYSTEM],

    version='6.1.4'
)

"""
Suitesparse.GraphBLAST installation information

[MUTABLE]

There are three ways to use suitesparse.
   - Use local version (SUITESPARSE.local)
   - Build it from sources, using GitHub repo (SUITESPARSE.repo)
   - Download binaries form conda repository (SUITESPARSE.download)

Before starting benchmarks choose exactly one way of usage
and set corresponding values to non-null values

"""
SUITESPARSE = Namespace(

    # Paths to the local version of suitesparse
    local=Namespace(
        # Path to the include directory (Ex. "../graphblas/include/")
        include=None,
        # Path to the library (Ex. "../graphblas/lib/libgraphblas.so")
        library=None
    ),

    # GitHub repository information
    repo=Namespace(
        url='https://github.com/DrTimothyAldenDavis/GraphBLAS',
        branch='v6.1.4',

        # Repository local path (where it will be cloned)
        dest=DEPS / 'suitesparse_graphblast',

        # Relative path to the include directory from the repository root
        include_rel=Path('Include'),

        # Relative path to the build directory, where the library will be built
        build_rel=Path('build'),

        # Relative path to the library binary
        library_rel=(Path('build') / 'libgraphblas').with_suffix(TARGET_SUFFIX)
    ),

    # Conda repository information
    download=None,

    # Uncomment, if you want to download the library
    # download=Namespace(
    #     url=f'https://anaconda.org/conda-forge/graphblas/{CONDA_GRB_REPO.version}/download/{CONDA_GRB_REPO.platform}/graphblas-{CONDA_GRB_REPO.version}-{CONDA_GRB_REPO.hash}_0.tar.bz2',
    #     dest=DEPS/'suitesparse_graphblast_conda',
    #     include_rel=Path('include'),
    #     library_rel=Path('lib') / 'libgraphblas' + TARGET_SUFFIX
    # )
)

"""
Build configurations
"""

BUILD = Namespace(
    # Paths to the C/C++/Cuda compilers (let Cmake detect by default)
    cc=None,
    cxx=None,
    cudacxx='/usr/bin/g++-8',

    # Number of jobs to build all sources (None will remove flag)
    jobs=6,
)

"""
Datasets configuration
"""


@dataclass
class DatasetSizeInfo:
    """
    Information about the size of the dataset
    """

    # Maximal number of edges for this category of dataset largeness
    max_n_edges: Optional[int]

    # Number of iterations for the algorithm to execute on the dataset of this size
    iterations: int


class DatasetSize(Enum):
    """
    Size configurations

    Change it to configure on how much iterations you want to
    run benchmark on dataset of this size

    [MUTABLE]
    """
    # `size` = DatasetSizeInfo(`max_edges`, `iterations`)
    tiny = DatasetSizeInfo(max_n_edges=5000, iterations=50)
    small = DatasetSizeInfo(max_n_edges=80000, iterations=20)
    medium = DatasetSizeInfo(max_n_edges=500000, iterations=10)
    large = DatasetSizeInfo(max_n_edges=2000000, iterations=5)
    extra_large = DatasetSizeInfo(max_n_edges=None, iterations=2)

    def iterations(self):
        return self.value.iterations

    def max_n_edges(self) -> Optional[int]:
        return self.value.max_n_edges

    def from_n_edges(n_edges: int):
        for d_size in list(DatasetSize):
            if d_size.max_n_edges() is None or d_size.max_n_edges() >= n_edges:
                return d_size
        raise Exception(f'Can not get largeness category of {n_edges} edges')


"""
Path to the file with the supportive information about datasets.
It includes if dataset is directed or not and what is the value type
in this dataset (void, float, int)

This file is created automatically

[MUTABLE]

"""
DATASETS_PROPERTIES = DATASET_FOLDER / 'properties.json'

"""
Urls of the datasets and their names
You may add more urls to test more tests

Note: Name of the dataset (key in this dictionary) must match
name of the .mtx file in the archive

Note: All datasets are taken from http://sparse.tamu.edu/

[MUTABLE]

"""
DATASET_URL: Dict[str, str] = {
    '1128_bus': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/1138_bus.tar.gz',
    'bcspwr03': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/bcspwr03.tar.gz',
    'soc-LiveJournal': 'https://suitesparse-collection-website.herokuapp.com/MM/SNAP/soc-LiveJournal1.tar.gz',
    'hollywood-09': 'https://suitesparse-collection-website.herokuapp.com/MM/LAW/hollywood-2009.tar.gz',
    'Journals': 'https://suitesparse-collection-website.herokuapp.com/MM/Pajek/Journals.tar.gz',
    'com-Orcut': 'https://suitesparse-collection-website.herokuapp.com/MM/SNAP/com-Orkut.tar.gz',
    'roadNet-CA': 'https://suitesparse-collection-website.herokuapp.com/MM/SNAP/roadNet-CA.tar.gz',
    'indochina-2004': 'https://suitesparse-collection-website.herokuapp.com/MM/LAW/indochina-2004.tar.gz',
    'cit-Patents': 'https://suitesparse-collection-website.herokuapp.com/MM/SNAP/cit-Patents.tar.gz',
    'coAuthorsCiteseer': 'https://suitesparse-collection-website.herokuapp.com/MM/DIMACS10/coAuthorsCiteseer.tar.gz',
    'coPapersDBLP': 'https://suitesparse-collection-website.herokuapp.com/MM/DIMACS10/coPapersDBLP.tar.gz'
}

"""
Default source for the path-finding algorithms (bfs, sssp)

[MUTABLE]

"""
DEFAULT_SOURCE = 0

"""
List of the datasets, which will be used for the benchmark
Name must correspond to the key in the DATASET_URL dictionary,
or to the .mtx

[MUTABLE]

"""
BENCHMARK_DATASETS = [
    '1128_bus',
    'bcspwr03',
    'soc-LiveJournal',
    'hollywood-09',
    'com-Orcut',
    'roadNet-CA',
    'indochina-2004',
    'cit-Patents',
    'coAuthorsCiteseer',
    'coPapersDBLP'
]

"""
Path to the benchmarks output directory

After each run of ./benchark.py script in the
BENCHMARK_OUTPUT will be created folder with the bechmark results
in .csv or .txt format. The folder will have name of the moment,
when benchmarks were executed. Also, a symlink BENCHMARK_OUTPUT/recent
will be created, which refers at the folder with the results
of the most recent benchmarks run.

[MUTABLE]

"""
BENCHMARK_OUTPUT = ROOT / 'benchmarks'


def jobs_flag() -> str:
    assert BUILD.jobs > 0
    if BUILD.jobs is None:
        return ''
    return f'-j{BUILD.jobs}'


def make_build_env() -> Dict[str, str]:
    env = os.environ.copy()

    additional_vars = {
        'CC': BUILD.cc,
        'CXX': BUILD.cxx,
        'CUDAHOSTCXX': BUILD.cudacxx
    }

    for k, v in additional_vars.items():
        if v is not None:
            env[k] = str(v)

    print(f'Using env: {additional_vars}')

    return env
