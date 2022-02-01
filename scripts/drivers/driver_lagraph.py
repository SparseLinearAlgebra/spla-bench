import os
import time

from typing import List

from drivers.driver import ExecutionResult, Driver
from lib.dataset import Dataset
from lib.algorithm import AlgorithmName
from lib.tool import ToolName
from lib.util import check_output


class DriverLaGraph(Driver):
    def can_run_bfs(self, dataset: Dataset) -> bool:
        raise NotImplementedError()

    def can_run_sssp(self, dataset: Dataset) -> bool:
        raise NotImplementedError()

    def can_run_tc(self, dataset: Dataset) -> bool:
        raise NotImplementedError()

    def run_bfs(self,
                dataset: Dataset,
                source_vertex: int,
                num_iterations: int) -> ExecutionResult:

        with TemporarySourcesFile([source_vertex + 1] * num_iterations) as sources_file:
            output = check_output([
                self.exec_path(AlgorithmName.bfs),
                dataset.path,
                sources_file.name
            ])

            return DriverLaGraph._parse_output(output, "parent only", 9, "warmup", 4)

    def run_sssp(self,
                 dataset: Dataset,
                 source_vertex: int,
                 num_iterations: int) -> ExecutionResult:

        with TemporarySourcesFile([source_vertex + 1] * num_iterations) as sources_file:
            output = check_output([
                self.exec_path(AlgorithmName.sssp),
                dataset.path,
                sources_file.name
            ])

            return DriverLaGraph._parse_output(output, "sssp", 8)

    def run_tc(self,
               dataset: Dataset,
               num_iterations: int) -> ExecutionResult:

        output = check_output([
            self.exec_path(AlgorithmName.tc),
            dataset.path
        ])

        return DriverLaGraph._parse_output(output, "trial ", 2, "nthreads: ", 3)

    def tool_name(self) -> ToolName:
        return ToolName.lagraph

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
            trials.append(float(tokenize(trial_line)[
                          trial_line_token]) * time_factor)
        warmup = 0
        if warmup_line_start is not None:
            warmup = float(tokenize(lines_startswith(lines, warmup_line_start)[0])[
                           warmup_line_token]) * time_factor
        return ExecutionResult(warmup, trials)


def lines_startswith(lines: List[str], token) -> List[str]:
    return list(filter(lambda s: s.startswith(token), lines))


def tokenize(line: str) -> List[str]:
    return list(filter(lambda x: x, line.split(' ')))


class TemporarySourcesFile():
    def __init__(self, sources: List[int]):
        self.name = f'sources_{str(time.ctime())}_.mtx'
        self.freeze = False
        self.fd = None
        self.sources = sources

    def __enter__(self):
        with open(self.name, 'wb') as sources_file:
            sources_file.write(make_sources_content(self.sources))
        return self

    def __exit__(self, type, value, traceback):
        if not self.freeze:
            os.remove(self.name)


def make_sources_content(sources: List[int]):
    n = len(sources)
    sources = '\n'.join(map(str, sources))

    return f'''
%%MatrixMarket matrix array real general
%-------------------------------------------------------------------------------
% Temporary sources file
%-------------------------------------------------------------------------------
{n} 1
{sources}
'''.encode('ascii')
