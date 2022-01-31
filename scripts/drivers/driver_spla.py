import drivers.driver as driver

from lib.dataset import Dataset
from lib.algorithm import AlgorithmName
from lib.tool import ToolName
from lib.dataset import DatasetValueType
from lib.util import check_output


class DriverSpla(driver.Driver):
    def can_run_bfs(self, dataset: Dataset) -> bool:
        return dataset.get_element_type() == DatasetValueType.void

    def can_run_sssp(self, dataset: Dataset) -> bool:
        return dataset.get_element_type() == DatasetValueType.float

    def can_run_tc(self, dataset: Dataset) -> bool:
        return True

    def run_bfs(self,
                dataset: Dataset,
                source_vertex: int,
                num_iterations: int) -> driver.ExecutionResult:

        output = check_output([
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

        output = check_output([
            self.exec_path(AlgorithmName.sssp),
            f"--mtxpath={dataset.path}",
            f"--niters={num_iterations}",
            f"--source={source_vertex}"
        ])

        return DriverSpla._parse_output(output)

    def run_tc(self,
               dataset: Dataset,
               num_iterations: int) -> driver.ExecutionResult:

        dir_flag = 'true' if not dataset.get_directed() else 'false'

        output = check_output([
            self.exec_path(AlgorithmName.tc),
            f"--mtxpath={dataset.path}",
            f"--niters={num_iterations}",
            f"--undirected={dir_flag}"
        ])
        return DriverSpla._parse_output(output)

    def tool_name(self) -> ToolName:
        return ToolName.spla

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
