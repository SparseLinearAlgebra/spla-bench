import subprocess

import drivers.driver as driver

from lib.dataset import Dataset
from lib.algorithm import AlgorithmName


class DriverSpla(driver.Driver):
    def can_run_bfs(self, dataset: Dataset) -> bool:
        raise NotImplementedError()

    def can_run_sssp(self, dataset: Dataset) -> bool:
        raise NotImplementedError()

    def can_run_tc(self, dataset: Dataset) -> bool:
        raise NotImplementedError()

    def run_bfs(self,
                dataset: Dataset,
                source_vertex: int,
                num_iterations: int) -> driver.ExecutionResult:

        output = subprocess.check_output([
            self.exec_path(AlgorithmName.bfs),
            f"--mtxpath={dataset.path}",
            f"--niters={num_iterations}",
            f"--source={source_vertex}"
        ])

        return DriverSpla._parse_output(output)

    def run_sssp(self,
                 dataset: Dataset,
                 source_vertex: int,
                 num_iterations: int) -> driver.ExecutionResult:

        output = subprocess.check_output([
            self.exec_path(AlgorithmName.sssp),
            f"--mtxpath={dataset.path}",
            f"--niters={num_iterations}",
            f"--source={source_vertex}"
        ])

        return DriverSpla._parse_output(output)

    def run_tc(self,
               dataset: Dataset,
               num_iterations: int) -> driver.ExecutionResult:

        output = subprocess.check_output([
            self.exec_path(AlgorithmName.tc),
            f"--mtxpath={dataset.path}",
            f"--niters={num_iterations}",
            f"--directed={int(dataset.get_directed)}"
        ])
        return DriverSpla._parse_output(output)

    def name(self) -> str:
        return 'spla'

    @staticmethod
    def _parse_output(output):
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        warmup = 0.0
        runs = []
        for line in lines:
            if line.startswith("warm-up(ms):"):
                warmup = float(line.split(" ")[1])
            if line.startswith("iters(ms):"):
                runs = [float(v) for v in line.split(" ")[1:-1]]
        return driver.ExecutionResult(warmup, runs)
