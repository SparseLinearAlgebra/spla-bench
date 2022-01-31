import subprocess

import drivers.driver as driver

from lib.dataset import Dataset
from lib.algorithm import AlgorithmName
from lib.tool import ToolName


class DriverGunrock(driver.Driver):
    def __init__(self):
        # type of the graph file, market (mtx) by default
        self.type = "market"
        # Device for evaluations
        self.device = 0

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

        output = check_output([str(self.exec_path(AlgorithmName.bfs)),
                               f"--src={source_vertex}",
                               f"--num-runs={num_iterations + 1}",
                               f"--undirected={int(not dataset.get_directed())}",
                               f"--graph-file={dataset.path}",
                               f"--graph-type={self.type}",
                               f"--device={self.device}"])
        return DriverGunrock._parse_output(output)

    def run_sssp(self,
                 dataset: Dataset,
                 source_vertex: int,
                 num_iterations: int) -> driver.ExecutionResult:

        output = check_output([str(self.exec_path(AlgorithmName.sssp)),
                               f"--src={source_vertex}",
                               f"--num-runs={num_iterations + 1}",
                               f"--undirected={int(not dataset.get_directed())}",
                               f"--graph-file={dataset.path}",
                               f"--graph-type={self.type}",
                               f"--device={self.device}"])
        return DriverGunrock._parse_output(output)

    def run_tc(self,
               dataset: Dataset,
               num_iterations: int) -> driver.ExecutionResult:

        output = check_output([str(self.exec_path(AlgorithmName.tc)),
                               f"--num-runs={num_iterations + 1}",
                               f"--undirected={int(not dataset.get_directed())}",
                               f"--graph-file={dataset.path}",
                               f"--graph-type={self.type}",
                               f"--device={self.device}"])
        return DriverGunrock._parse_output(output)

    def tool_name(self) -> ToolName:
        return ToolName.gunrock

    @staticmethod
    def _parse_output(output):
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        runs = []
        for line in lines:
            if line.startswith("Run ") and not line.startswith("Run CPU"):
                runs.append(float(line.split(" ")[3]))
        # First one is warm-up (we add it implicitly)
        return driver.ExecutionResult(runs[0], runs[1:])
