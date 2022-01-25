import subprocess

import driver
import shared

__all__ = [
    "DriverGunrock"
]


class DriverGunrock(driver.Driver):

    def __init__(self):
        self.exec_dir = shared.DEPS / "gunrock" / "build" / "bin"
        self.bfs = "bfs"
        self.sssp = "sssp"
        self.tc = "tc"

        # type of the graph file, market (mtx) by default
        self.type = "market"
        # Device for evaluations
        self.device = 0
        # Type of graph
        self.undirected = 0

    def run_bfs(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.bfs),
                                          f"--src={source_vertex}",
                                          f"--num-runs={num_iterations + 1}",
                                          f"--undirected={self.undirected}",
                                          f"--graph-file={matrix_path}",
                                          f"--graph-type={self.type}",
                                          f"--device={self.device}"])
        return DriverGunrock._parse_output(output)

    def run_sssp(self, matrix_path, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.sssp),
                                          f"--src={source_vertex}",
                                          f"--num-runs={num_iterations + 1}",
                                          f"--undirected={self.undirected}",
                                          f"--graph-file={matrix_path}",
                                          f"--graph-type={self.type}",
                                          f"--device={self.device}"])
        return DriverGunrock._parse_output(output)

    def run_tc(self, matrix_path, num_iterations, directed) -> driver.ExecutionResult:
        output = subprocess.check_output([str(self.exec_dir / self.sssp),
                                          f"--num-runs={num_iterations + 1}",
                                          f"--undirected={self.undirected}",
                                          f"--graph-file={matrix_path}",
                                          f"--graph-type={self.type}",
                                          f"--device={self.device}"])
        return DriverGunrock._parse_output(output)

    @staticmethod
    def _parse_output(output):
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        runs = []
        for line in lines:
            if line.startswith("Run ") and not line.startswith("Run CPU"):
                runs.append(float(line.split(" ")[3]))
        # First one is warm-up (we add it implicitly)
        return driver.ExecutionResult(runs[0], runs[1:])
