#!/usr/bin/env python3

import argparse

from typing import List

import config
import lib.util as util

from lib.algorithm import AlgorithmName
from lib.tool import ToolName
from lib.dataset import Dataset
from lib.benchmark_summary import BenchmarkSummary, OutputFormat, ResultsPrinter
from drivers.driver_graphblast import DriverGraphBLAST
from drivers.driver_gunrock import DriverGunrock
from drivers.driver_lagraph import DriverLaGraph
from drivers.driver_spla import DriverSpla
from drivers.driver import Driver


def tool_to_driver(tool: ToolName) -> Driver:
    drivers = {
        ToolName.spla: lambda _: DriverSpla(),
        ToolName.lagraph: lambda _: DriverLaGraph(),
        ToolName.gunrock: lambda _: DriverGunrock(),
        ToolName.graphblast: lambda _: DriverGraphBLAST(),
    }
    return drivers[tool](None)


def main():
    parser = argparse.ArgumentParser(
        description='Bebchmarking tool for the graph algorithms')

    parser.add_argument('--algo',
                        type=AlgorithmName,
                        choices=list(AlgorithmName),
                        help='Select algorithm to run (otherwise all algorithms are benchmarked)')
    parser.add_argument('--tool',
                        type=ToolName,
                        choices=list(ToolName),
                        help='Select tool to use (otherwise all tools are benchmarked)')
    parser.add_argument('--output',
                        default=config.BENCHMARK_OUTPUT,
                        help='File to dump benchmark results')
    parser.add_argument('--format',
                        type=OutputFormat,
                        choices=list(OutputFormat),
                        default=OutputFormat.csv,
                        help='Format to dump benchmark results')
    parser.add_argument('--printer',
                        type=ResultsPrinter,
                        choices=list(ResultsPrinter),
                        default=ResultsPrinter.all,
                        help='Measurement printer')

    args = parser.parse_args()

    drivers: List[Driver] = []
    if args.tool is None:
        drivers = map(tool_to_driver, list(ToolName))
    else:
        drivers = [tool_to_driver(args.tool)]

    algorithms: List[AlgorithmName] = []
    if args.algo is None:
        algorithms = list(AlgorithmName)
    else:
        algorithms = [args.algo]

    def print_status(status: str, *args):
        util.print_status('benchmark', status, *args)

    summary = BenchmarkSummary()

    try:
        for dataset_name in config.BENCHMARK_DATASETS:
            print_status(f'dataset {dataset_name}', 'start preparation')
            dataset = Dataset(dataset_name)
            print_status(f'dataset {dataset_name}', 'finish preparation')

            for algo in algorithms:
                status_algo_dataset = f'algo: {algo}, dataset: {dataset.name}'

                print_status(status_algo_dataset,
                             'check if all tools can be used')

                all_can_run = all(map(
                    lambda driver: driver.can_run(dataset, algo), drivers
                ))

                if not all_can_run:
                    print_status(status_algo_dataset,
                                 f'not runnable on some drivers, skipping')
                    continue

                print_status(status_algo_dataset, 'start benchmarking')
                for driver in drivers:
                    status = f'algo: {algo}, dataset: {dataset.name}, tool: {str(driver.tool_name())}'
                    print_status(status, 'start benchmarking')
                    result = driver.run(dataset, algo)
                    print_status(status, 'finish benchmarking')
                    summary.add_measurement(
                        driver.tool_name(), dataset, algo, result)
                print_status(status_algo_dataset, 'finish benchmarking')
    finally:
        summary.dump(args.format, args.output, args.printer)


if __name__ == '__main__':
    main()
