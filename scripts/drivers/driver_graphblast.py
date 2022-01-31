import subprocess

import drivers.driver as driver
import config

from lib.algorithm import AlgorithmName
from lib.tool import ToolName
from lib.dataset import Dataset
from lib.util import check_output


class DriverGraphBLAST(driver.Driver):
    def __init__(self):
        self_config = config.TOOL_CONFIG[ToolName.graphblast].config

        self.timing = self_config.timing
        self.skip_cpu_verify = int(self_config.skip_cpu_verify)

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

        directed_flag = 1 if dataset.get_directed() else 2

        output = check_output([str(self.exec_path(AlgorithmName.bfs)),
                               f"--source={source_vertex}",
                               f"--niter={num_iterations}",
                               f"--timing={self.timing}",
                               f"--directed={directed_flag}",
                               f"--skip_cpu_verify={self.skip_cpu_verify}",
                               str(dataset.path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    def run_sssp(self,
                 dataset: Dataset,
                 source_vertex: int,
                 num_iterations: int) -> driver.ExecutionResult:

        directed_flag = 1 if dataset.get_directed() else 2

        output = check_output([str(self.exec_path(AlgorithmName.sssp)),
                               f"--source={source_vertex}",
                               f"--niter={num_iterations}",
                               f"--timing={self.timing}",
                               f"--directed={directed_flag}",
                               f"--skip_cpu_verify={self.skip_cpu_verify}",
                               str(dataset.path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    def run_tc(self,
               dataset: Dataset,
               num_iterations: int) -> driver.ExecutionResult:

        directed_flag = 1 if dataset.get_directed() else 2

        output = check_output([str(self.exec_path(AlgorithmName.tc)),
                               f"--niter={num_iterations}",
                               f"--timing={self.timing}",
                               f"--directed={directed_flag}",
                               f"--skip_cpu_verify={self.skip_cpu_verify}",
                               str(dataset.path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    def tool_name(self) -> ToolName:
        return ToolName.graphblast

    @staticmethod
    def _parse_output(output, n):
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        warmup = 0.0
        tight = 0.0
        for line in lines:
            if line.startswith("warmup"):
                warmup = float(line.replace(",", "").split(" ")[1])
            if line.startswith("tight"):
                # TODO: is it correct?..
                tight = float(line.replace(",", "").split(" ")[1])

        return driver.ExecutionResult(warmup, [tight] * n)
