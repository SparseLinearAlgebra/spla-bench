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

> Note: SuiteSparse library must be installed on your system in order to build and run (2) benchmarks

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

### Download dataset

The following code snippet allows downloading, unpack and store locally all required
graph matrices for benchmarking. Downloading is done by `dataset.py` script inside `scripts` folder.
Must be executed inside root folder.

```shell
$ python3 scripts/dataset.py --all
```

See `-h` option to get more info about available script features.
Must be executed inside root folder.

```shell
$ python3 scripts/dataset.py -h

usage: dataset.py [-h] [--all] [--name NAME] [--url URL] [--print] [--ignore_cached]

optional arguments:
  -h, --help       show this help message and exit
  --all            Download all datasets
  --name NAME      Download dataset by name
  --url URL        Download dataset by url
  --print          Print all default datasets
  --ignore_cached  Ignore cached datasets
```

## Directory structure

```
spla
├── .github - GitHub Actions CI/CD setup 
├── docs - documents, text files and various helpful stuff
├── ide - files to setup local ide for development 
├── scripts - python sripts to prepare and run benchmarks
├── deps - benchmark third-party tools to test
│   ├── spla - SPLA library (submodule)
│   ├── lagraph - LAGraph library (submodule)
│   ├── graphblast - GraphBLAST library (submodule)
│   └── gunrock - Gunrock library (submodule)
└── CMakeLists.txt - library cmake config, add this as sub-directory to your project
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
