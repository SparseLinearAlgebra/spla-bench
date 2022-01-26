import os
import pathlib
import subprocess
import re

from typing import List

import shared

from driver import ExecutionResult, Driver

__all__ = [
    "DriverLaGraph"
]


class DriverLaGraph(Driver):
    """
    LaGraph library driver
    Use `BENCH_DRIVER_LAGRAPH` env variable to specify custom path to lagraph driver
    """

    def __init__(self, lagraph_build_root: pathlib.Path):
        self.exec_dir = lagraph_build_root / "src" / "benchmark"
        if not os.path.exists(self.exec_dir):
            raise Exception(f'LaGraph exec dir does not exist, where it should be: {self.exec_dir}')
        self.lagraph_bfs = "bfs_demo" + shared.EXECUTABLE_EXT
        self.lagraph_sssp = "sssp_demo" + shared.EXECUTABLE_EXT
        self.lagraph_tc = "tc_demo" + shared.EXECUTABLE_EXT

        try:
            self.exec_dir = pathlib.Path(os.environ["BENCH_DRIVER_LAGRAPH"])
            print("Set lagraph exec dir to:", self.exec_dir)
        except KeyError:
            pass

    def run_bfs(self, matrix_path) -> ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.lagraph_bfs), matrix_path])
        return DriverLaGraph._parse_output(output, "parent only", 9, "warmup", 4)

    def run_sssp(self, matrix_path) -> ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.lagraph_sssp), matrix_path])
        return DriverLaGraph._parse_output(output, "sssp", 8)

    def run_tc(self, matrix_path) -> ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.lagraph_tc), matrix_path])
        return DriverLaGraph._parse_output(output, "trial ", 2, "nthreads: ", 3)

    @staticmethod
    def _parse_output(output: bytes,
                      trial_line_start: str,
                      trial_line_token: int,
                      warmup_line_start: str = None,
                      warmup_line_token: int = None):
        time_factor = 1000
        lines = output.decode("ASCII").split("\n")
        trials = []
        for trial_line in lines_startswith(lines, trial_line_start):
            trials.append(float(tokenize(trial_line)[trial_line_token]) * time_factor)
        warmup = 0
        if warmup_line_start is not None:
            warmup = float(tokenize(lines_startswith(lines, warmup_line_start)[0])[warmup_line_token]) * time_factor
        return ExecutionResult(warmup, trials)


def lines_startswith(lines: List[str], token) -> List[str]:
    return list(filter(lambda s: s.startswith(token), lines))


def tokenize(line: str) -> List[str]:
    return list(filter(lambda x: x, line.split(' ')))
