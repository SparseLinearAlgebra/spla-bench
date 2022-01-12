cmake_minimum_required(VERSION 3.10)
project(spla-bench CXX)

# By default, all options are enabled.
# If you want to disable some tool benchmarks build, do:
#  - In ide project settings -> cmake -> pass custom options
#  - In console build pass -D... options to cmake
option(BENCH_WITH_SPLA "Include <spla> in benchmark build" YES)
option(BENCH_WITH_SUITESPARSE "Include <suitesparse> in benchmark build" YES)
option(BENCH_WITH_GRAPHBLAST "Include <graphblast> in benchmark build" YES)
option(BENCH_WITH_GUNROCK "Include <gunrock> in benchmark build" YES)

# Use this vars to set sources specific to the tested tool
set(BENCH_SOURCES_SPLA)
set(BENCH_SOURCES_SUITESPARSE)
set(BENCH_SOURCES_GRAPHBLAST)
set(BENCH_SOURCES_GUNROCK)

if (BENCH_WITH_SPLA)
    message(STATUS "Add <spla> source to benchmark build")
    set(BENCH_SOURCES_SPLA
            sources/plugins/spla/PluginSpla.cpp
            sources/plugins/spla/PluginSpla.hpp
            )

endif (BENCH_WITH_SPLA)

if (BENCH_WITH_SUITESPARSE)
    message(STATUS "Add <suitesparse> source to benchmark build")

endif (BENCH_WITH_SUITESPARSE)

if (BENCH_WITH_GRAPHBLAST)
    message(STATUS "Add <graphblast> source to benchmark build")

endif (BENCH_WITH_GRAPHBLAST)

if (BENCH_WITH_GUNROCK)
    message(STATUS "Add <gunrock> source to benchmark build")

endif (BENCH_WITH_GUNROCK)

set(BENCH_SOURCES
        sources/Main.cpp
        sources/Plugin.hpp
        sources/Benchmark.hpp
        sources/BenchmarkParams.hpp
        sources/BenchmarkEngine.cpp
        sources/BenchmarkEngine.hpp
        sources/data/GraphData.hpp
        sources/data/GraphLoader.cpp
        sources/data/GraphLoader.hpp
        )

list(APPEND BENCH_SOURCES ${BENCH_SOURCES_SPLA})
list(APPEND BENCH_SOURCES ${BENCH_SOURCES_SUITESPARSE})
list(APPEND BENCH_SOURCES ${BENCH_SOURCES_GRAPHBLAST})
list(APPEND BENCH_SOURCES ${BENCH_SOURCES_GUNROCK})

add_executable(spla_bench ${BENCH_SOURCES})
target_include_directories(spla_bench PRIVATE "sources")