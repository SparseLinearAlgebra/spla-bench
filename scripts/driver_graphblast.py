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

        # 0: do not display per iteration timing, 1: display per iteration timing
        self.timing = 0
        # 0: follow mtx, 1: force undirected graph to be directed, 2: force directed graph to be undirected
        self.directed = 0
        # 0: run CPU verification, 1: skip CPU algorithm verification
        self.skip_cpu_verify = 0

    def run_bfs(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.gbfs),
                                          f"--source={source_vertex}",
                                          f"--niter={num_iterations}",
                                          f"--timing={self.timing}",
                                          f"--directed={self.directed}",
                                          f"--skip_cpu_verify={self.skip_cpu_verify}",
                                          str(matrix_path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    def run_sssp(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.gsssp),
                                          f"--source={source_vertex}",
                                          f"--niter={num_iterations}",
                                          f"--timing={self.timing}",
                                          f"--directed={self.directed}",
                                          f"--skip_cpu_verify={self.skip_cpu_verify}",
                                          str(matrix_path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    def run_tc(self, matrix_path, num_iterations, directed) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.gsssp),
                                          f"--niter={num_iterations}",
                                          f"--timing={self.timing}",
                                          f"--directed={self.directed}",
                                          f"--skip_cpu_verify={self.skip_cpu_verify}",
                                          str(matrix_path)])
        return DriverGraphBLAST._parse_output(output, num_iterations)

    @staticmethod
    def _parse_output(output, n):
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        warmup = 0.0
        tight = 0.0
        for line in lines:
            if line.startswith("warmup"):
                warmup = float(line.replace(",", "").split(" ")[1])
            if line.startswith("tight"):
                tight = float(line.replace(",", "").split(" ")[1])

        return driver.ExecutionResult(warmup, [tight] * n)
