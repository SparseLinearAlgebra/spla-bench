from enum import Enum


class AlgorithmName(Enum):
    bfs = 'bfs'
    tc = 'tc'
    sssp = 'sssp'

    def __str__(self):
        return self.value
