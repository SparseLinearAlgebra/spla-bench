import subprocess

import driver
import shared

__all__ = [
    "DriverGraphBLAST"
]


class DriverGraphBLAST(driver.Driver):

    def __init__(self):
        self.exec_dir = shared.DEPS / "graphblast" / "bin"
        self.gbfs = "gbfs"
        self.gsssp = "gsssp"
        self.gtc = "gtc"

        self.timing = 0
        self.directed = 0

    def run_bfs(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.gbfs),
                                          f"--source={source_vertex}",
                                          f"--niter={num_iterations}",
                                          f"--timing={self.timing}",
                                          f"--directed={self.directed}",
                                          str(matrix_path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    def run_sssp(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        pass

    def run_tc(self, matrix_path, num_iterations, directed) -> driver.ExecutionResult:
        pass

    @staticmethod
    def _parse_output(output, n):
        lines = output.decode("ASCII").replace("\r", "").split("\n")

        warmup = 0.0
        tight = 0.0

        for line in lines:
            if line.startswith("warmup"):
                warmup = line.replace(",", "").split(" ")[1]
            if line.startswith("tight"):
                tight = line.replace(",", "").split(" ")[1]

        return driver.ExecutionResult(warmup, [tight] * n)
