import os
import pathlib
import subprocess
import re

from typing import List

import driver
import shared

__all__ = [
    "DriverLaGraph"
]


class DriverLaGraph(driver.Driver):
    """
    LaGraph library driver
    Use `BENCH_DRIVER_LAGRAPH` env variable to specify custom path to lagraph driver
    """

    def __init__(self):
        self.exec_dir = shared.DEPS / "lagraph" / "build" / "src" / "benchmark"
        self.lagraph_bfs = "bfs_demo" + shared.EXECUTABLE_EXT
        self.lagraph_sssp = "sssp_demo" + shared.EXECUTABLE_EXT
        self.lagraph_tc = "tc_demo" + shared.EXECUTABLE_EXT

        try:
            self.exec_dir = pathlib.Path(os.environ["BENCH_DRIVER_LAGRAPH"])
            print("Set lagraph exec dir to:", self.exec_dir)
        except KeyError:
            pass

    def run_bfs(self, matrix_path) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.lagraph_bfs), matrix_path])
        return DriverLaGraph._parse_output(output, "parent only ", 9, "nthreads: ", 2)

    def run_sssp(self, matrix_path) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.lagraph_sssp), matrix_path])
        return DriverLaGraph._parse_output(output, "sssp", 8)

    def run_tc(self, matrix_path) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.lagraph_tc), matrix_path])
        return DriverLaGraph._parse_output(output, "trial ", 2, "nthreads: ", 3)

    @staticmethod
    def _parse_output(output: bytes,
                      trial_line_start: str,
                      trial_line_token: int,
                      warmup_line_start: str = None,
                      warmup_line_token: int = None):
        lines = output.decode("ASCII").split("\n")
        trials = []
        for trial_line in lines_startswith(lines, trial_line_start):
            trials.append(float(tokenize(trial_line)[trial_line_token]) * 1000)
        warmup = 0
        if warmup_line_start is not None:
            warmup = float(tokenize(lines_startswith(lines, warmup_line_start)[0])[warmup_line_token]) * 1000
        return driver.ExecutionResult(warmup, trials)


def lines_startswith(lines: List[str], token) -> List[str]:
    return list(filter(lambda s: s.startswith(token), lines))


def tokenize(line: str) -> List[str]:
    return list(filter(lambda x: x, line.split(' ')))


import sys


def main():
    path = sys.argv[1]
    driver = DriverLaGraph()
    print(driver.run_bfs(path))
