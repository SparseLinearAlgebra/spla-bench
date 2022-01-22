import os
import pathlib
import subprocess

import driver
import shared


class DriverSpla(driver.Driver):
    """
    SPLA library driver.
    Use `BENCH_DRIVER_SPLA` env variable to specify custom path to spla driver
    """

    def __init__(self):
        self.exec_dir = shared.DEPS / "spla" / "build"
        self.spla_bfs = "spla_bfs" + shared.EXECUTABLE_EXT
        self.spla_sssp = "spla_sssp" + shared.EXECUTABLE_EXT
        self.spla_tc = "spla_tc" + shared.EXECUTABLE_EXT

        try:
            self.exec_dir = pathlib.Path(os.environ["BENCH_DRIVER_SPLA"])
            print("Set spla exec dir to:", self.exec_dir)
        except KeyError:
            pass

    def run_bfs(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_bfs),
             f"--mtxpath={matrix_path}",
             f"--niters={num_iterations}",
             f"--source={source_vertex}"])
        return DriverSpla._parse_output(output)

    def run_sssp(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_sssp),
             f"--mtxpath={matrix_path}",
             f"--niters={num_iterations}",
             f"--source={source_vertex}"])
        return DriverSpla._parse_output(output)

    def run_tc(self, matrix_path, num_iterations, directed) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_sssp),
             f"--mtxpath={matrix_path}",
             f"--niters={num_iterations}",
             f"--directed={directed}"])
        return DriverSpla._parse_output(output)

    @staticmethod
    def _parse_output(output):
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        warm_up = float(lines[0].split(" ")[1])
        times = [float(v) for v in lines[1].split(" ")[1:-1]]
        return driver.ExecutionResult(warm_up, times)
