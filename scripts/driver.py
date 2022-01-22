import abc

__all__ = [
    "ExecutionResult",
    "Driver"
]


class ExecutionResult:
    """
    Result of the execution of the single algorithm benchmark run
    """
    __slots__ = ["warm_up", "times"]

    def __init__(self, warm_up, times):
        self.warm_up = warm_up
        self.times = times

    def __repr__(self):
        return f"warm_up(ms)={self.warm_up} times(ms)={self.times}"


class Driver:
    """
    Base class for any driver, which is responsible for running
    algorithm benchmarks for third-party tools from stand-alone
    executable files.

    Algorithms:
        * bfs
        * sssp
        * tc
        * [future] cc
        * [future] page rank
    """

    @abc.abstractmethod
    def run_bfs(self, matrix_path, source_vertex, num_iterations) -> ExecutionResult:
        """
        Run bfs algorithm benchmark.

        :param matrix_path: Path to file with matrix in .mtx format
        :param source_vertex: Source vertex to start algorithm
        :param num_iterations: Number of iteration to run
        :return: execution results
        """
        pass

    @abc.abstractmethod
    def run_sssp(self, matrix_path, source_vertex, num_iterations) -> ExecutionResult:
        """
        Run sssp algorithm benchmark.

        :param matrix_path: Path to file with matrix in .mtx format
        :param source_vertex: Source vertex to start algorithm
        :param num_iterations: Number of iteration to run
        :return: execution results
        """
        pass

    @abc.abstractmethod
    def run_tc(self, matrix_path, num_iterations, directed) -> ExecutionResult:
        """
        Run tc algorithm benchmark.

        :param matrix_path: Path to file with matrix in .mtx format
        :param num_iterations: Number of iteration to run
        :param directed: True if graph is directed
        :return: execution results
        """
        pass
