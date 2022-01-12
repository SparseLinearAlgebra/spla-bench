# spla-bench

[![JB Research](https://jb.gg/badges/research-flat-square.svg)](https://research.jetbrains.org/)
[![Clang Format](https://github.com/JetBrains-Research/spla-bench/actions/workflows/clang-format.yml/badge.svg?branch=main)](https://github.com/JetBrains-Research/spla-bench/actions/workflows/clang-format.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/JetBrains-Research/spla-bench/blob/master/LICENSE.md)

Benchmark suite for performance analysis of sparse graphs frameworks.
Part of the Spla research project.

### Benchmark algorithms

- BFS (breadth-first search) for directed graphs with arbitrary values (only structure required)
- SSSP (single-source the shortest paths) for directed graphs with float values
- TC (triangles counting) for directed graphs (integer values stored)
- **Future:** CC (connected componets)
- **Future:** PageRank

### Frameworks

- (1) [Spla](https://github.com/JetBrains-Research/spla) - Generalized sparse linear algebra framework for multi-GPU computations
- (2) [GraphBLAS:SuiteSparse](https://github.com/DrTimothyAldenDavis/SuiteSparse) - Suite of sparse matrix algorithms authored or co-authored by Tim Davis, Texas A&M University
- (3) [GraphBLAST](https://github.com/gunrock/graphblast) - High-Performance Linear Algebra-based Graph Primitives on GPUs
- (4) [Gunrock](https://github.com/gunrock/gunrock) - High-Performance Graph Primitives on GPUs

> Note: SuiteSparse library must be installed on your system in order to build and run (2) benchmarks

> Note: CUDA SDK must be installed on your system in order to build and run (3) (4) benchmarks

### Dataset

Matrices from the SuiteSparse Matrix Collection (formerly the University of Florida Sparse Matrix Collection).

## Build instructions

### Get source code

The following code snippet downloads project source code repository, enters project root folder
and runs submodules init in order to get dependencies source code initialized.
Must be executed from the folder where you want to locate project.

```shell
$ git clone https://github.com/JetBrains-Research/spla-bench.git
$ cd spla-bench
$ git submodule update --init --recursive
```

### Configure and run build

The following code snippet runs cmake build configuration process
with output into `build` directory, in `Release` mode with all tools build enabled.
Then runs build process for `build` directory in verbose mode with `-j 4` four system threads.
Must be executed from project root folder.

```shell
$ cmake . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
$ cmake --build build --target all --verbose -j 4
```

Pass extra options to disable build of some tools:
 - `-DBENCH_WITH_SPLA=NO` - exclude <spla> in benchmark build (default YES)
 - `-DBENCH_WITH_SUITESPARSE=NO` - exclude <suitesparse> in benchmark build (default YES)
 - `-DBENCH_WITH_GRAPHBLAST=NO` - exclude <graphblast> in benchmark build (default YES)
 - `-DBENCH_WITH_GUNROCK=NO` - exclude <gunrock> in benchmark build (default YES)

## Directory structure

```
spla
├── .github - GitHub Actions CI/CD setup 
├── docs - documents, text files and various helpful stuff
├── ide - files to setup local ide for development 
├── scripts - python sripts to prepare and run benchmarks
├── sources - source code for library implementation
│   └── plugins - folder with tested tool
│       ├── spla - benchmarks implementation for Spla library
│       ├── suitesparse - benchmarks implementation for GraphBLAS:SuiteSparse library 
│       ├── graphblast - benchmarks implementation for GraphBLAST library
│       └── gunrock - benchmarks implementation for Gunrock library
├── deps - benchmark third-party tools
│   ├── spla - SPLA library (submodule)
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
