# spla-bench

[![JB Research](https://jb.gg/badges/research-flat-square.svg)](https://research.jetbrains.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/JetBrains-Research/spla-bench/blob/master/LICENSE.md)

Benchmark suite for performance analysis of sparse graphs frameworks.
Part of the Spla research project.

### Benchmark algorithms

- BFS (breadth-first search) for directed graphs with arbitrary values (only structure required)
- SSSP (single-source the shortest paths) for directed graphs with float values
- TC (triangles counting) for directed graphs (integer values stored)
- **Future:** CC (connected components)
- **Future:** PageRank

### Frameworks

- (1) [Spla](https://github.com/JetBrains-Research/spla) - Generalized sparse linear algebra framework for multi-GPU computations
- (2) [LAGraph](https://github.com/GraphBLAS/LAGraph) - Linear algebra graph algorithms on top of the GraphBLAS SuiteSparse
- (3) [GraphBLAST](https://github.com/gunrock/graphblast) - High-Performance Linear Algebra-based Graph Primitives on GPUs
- (4) [Gunrock](https://github.com/gunrock/gunrock) - High-Performance Graph Primitives on GPUs

> Note: OpenCL SDK and Boost must be installed to build and run (1) benchmarks

> Note: CUDA SDK must be installed on your system in order to build and run (3) (4) benchmarks

### Dataset

Matrices from the SuiteSparse Matrix Collection (formerly the University of Florida Sparse Matrix Collection).
Datasets could be downloaded from [sparse.tamu.edu](https://sparse.tamu.edu/).

## Instructions

### Get source code

The following code snippet downloads project source code repository, enters project root folder
and runs submodules init in order to get dependencies source code initialized.
Must be executed from the folder where you want to locate project.

```shell
$ git clone https://github.com/JetBrains-Research/spla-bench.git
$ cd spla-bench
$ git submodule update --init --recursive
```

### Build third-party tools

The first time benchmarks are run, those and only those libraries that will be needed for the benchmark will be automatically built. They will be built accordingly to the [`scripts/config.py`](./scripts/config.py) file. Therefore, if you want to modify default build settings, please see this configuration file and change configuration variables which are marked `[MUTABLE]`.

> Note: It is highly recommended to visit the configuration file [`scripts/config.py`](./scripts/config.py) and study meaning of settings and see if they match your desires.

Meanwhile, you also can build any particular tool. To do that, use [`scripts/build_tool.py`](./scripts/build_tool.py)

```shell
$ ./scripts/build_tool.py -h
usage: Third party libraries building tool [-h] [-j J] [--cc CC] [--cxx CXX] [--cudacxx CUDACXX]
                                           {graphblast,spla,lagraph,gunrock}

positional arguments:
  {graphblast,spla,lagraph,gunrock}
                        Select tool to build

optional arguments:
  -h, --help            show this help message and exit
  -j J                  Number of jobs to build
  --cc CC               Path to the C compiler
  --cxx CXX             Path to the C++ compiler
  --cudacxx CUDACXX     Path to the Cuda compiler
```

> Note: `scripts/build_tool.py` flags will override `scripts/config.py` build settings

#### GraphBLAST

Prerequisites:
 - Cuda Toolkit
 - Compatible GCC (8 for CUDA 10)
 - Boost library
 - Make

#### Gunrock

Prerequisites:
- Cuda Toolkit
- Compatible GCC (8 for CUDA 10)
- Boost library
- CMake & Make


#### Spla

Prerequisites:
- C++ Compiler with C++ 17 support
- OpenCL 1.2+ SDK
- Boost library
- CMake & Make

#### LaGraph

Prerequisites:
- Make
- C++ Compiler which is visible by Make
- GraphBLAS

To run lagraph you need to have GraphBLAS installed. But it is not necessarily should exist on your computer before benchmark execution.
There are three ways to give GraphBLAS to the LaGraph:

- Configure GraphBLAS headers and library path in the [`scripts/config.py`](scripts/config.py) file - variable `SUITESPARSE.local`

- (Default) Built it from sources from GitHub - `SUITESPARSE.repo`

- Download binaries and library from conda repo - `SUITESPARSE.download`

> Note: You must choose exactly one way. Otherwise, the building script will not know which way of installation to use

Visit [`scripts/config.py`](scripts/config.py) to see how exactly configure this variables.

### Add the datasets

There are two ways to use dataset in the benchmarks

#### Download

All of the used datasets downloaded also automatically when needed. To add more datasets to the benchmark, add more urls to the `DATASET_URL` dictionary in the [`scripts/config.py`](./scripts/config.py) file.

#### Use local

You also can test your local `.mtx` dataset. To do this, add a JSON object, which describes your dataset to the `DATASETS_PROPERTIES` file (`/dataset/properties.json` by default). For example:

```json
"1128_bus": {
    "path": "/some/absolute/local/path/dataset_name.mtx",

// Set the following fields only if you sure. Otherwise, you may not add the particular field
    "element_type": "void", // (float, int)
    "directed": true
}
```

After you set the dataset url, or configured its the local version, please add its name to the `BENCHMARK_DATASETS` list in the [`scripts/config.py`](./scripts/config.py). This list represents datasets, on which the bechmarks will be run. 

> Note: Name of the dataset (key in this dictionary) must match
name of the `.mtx` file in the archive

### Execute benchmarks

To execute benchmarks, use [`scripts/benchmark.py`](./scripts/benchmark.py) script.

To run benchmarks, just execute it

```shell
$ ./scripts/benchmark.py -h
usage: benchmark.py [-h] [--algo {bfs,tc,sssp}] [--tool {graphblast,spla,lagraph,gunrock}] [--output OUTPUT]
                    [--format {OutputFormat.raw,OutputFormat.csv}] [--printer {all,median}]

Bebchmarking tool for the graph algorithms

optional arguments:
  -h, --help            show this help message and exit
  --algo {bfs,tc,sssp}  Select algorithm to run (otherwise all algorithms are benchmarked)
  --tool {graphblast,spla,lagraph,gunrock}
                        Select tool to use (otherwise all tools are benchmarked)
  --output OUTPUT       File to dump benchmark results
  --format {OutputFormat.raw,OutputFormat.csv}
                        Format to dump benchmark results
  --printer {all,median}
                        Measurement printer
```

As you can see, it has different run configurations.
They all described in the help section. It is worth mentioning, that `printer` configures information, which is printed about each run.

- `all` will print all information: average time, median and standard deviation
- `median` will print only the median time


#### How the benchmark works

You tell it which algorithms you want to use.
All the specified algorithms will be built automatically, using a configuration file [`scripts/config.py`](scripts/config.py). If required executables are already built, they won't be rebuilt.

Before using each dataset, the script will
extract additional information about it: if the graph is directed and what is the type of the values on the edges. Retrieved information will
be stored in the properties file ([`datasets/properties.json`](datasets/properties.json) by default)


The script also accepts information about which algorithms you want to test.
Therefore, if the build finishes without any errors, it will start testing each algorithm on every possible dataset (if it fits it by orientation, weighting).

When testing ends (or an exception is thrown), information about runs is dumped to a folder (`benchmarks/${current_time}/` by default).
For convenience, a symlink is created to the folder where the results with the latest results are stored (`benchmarks/recent/`).

## Directory structure

```
spla-bench
├── dataset - Datasets and their properties
├── docs - documents, text files and various helpful stuff
├── deps - benchmark third-party tools to test
│   ├── spla - SPLA library (submodule)
│   ├── lagraph - LAGraph library (submodule)
│   ├── graphblast - GraphBLAST library (submodule)
│   └── gunrock - Gunrock library (submodule)
├── ide - files to setup local ide for development 
└── scripts - python sripts to prepare and run benchmarks
```

## Contributors

- Egor Orachyov (Github: [@EgorOrachyov](https://github.com/EgorOrachyov))
- Gleb Marin (Github: [@Glebanister](https://github.com/Glebanister))
- Semyon Grigorev (Github: [@gsvgit](https://github.com/gsvgit))

## Citation

```ignorelang
@online{spla-bench,
  author = {Orachyov, Egor and Marin, Gleb and Grigorev, Semyon},
  title = {spla bench: suite of benchmarks for spla project},
  year = 2021,
  url = {https://github.com/JetBrains-Research/spla-bench},
  note = {Version 0.0.0}
}
```

## License

This project licensed under MIT License. License text can be found in the
[license file](https://github.com/JetBrains-Research/spla-bench/blob/master/LICENSE.md).

## Acknowledgments <img align="right" width="15%" src="https://github.com/JetBrains-Research/spla-bench/raw/main/docs/logos/jetbrains-logo.png?raw=true&sanitize=true">

This is a research project of the Programming Languages and Tools Laboratory
at JetBrains-Research. Laboratory website [link](https://research.jetbrains.org/groups/plt_lab/).
