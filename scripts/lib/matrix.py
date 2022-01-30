import random

from typing import List, Tuple, Union, Callable, Type, Optional
from pathlib import Path


MatrixValueType = Union[int, float]
ValuedMatrixEntry = Tuple[int, int, MatrixValueType]
VoidMatrixEntry = Tuple[int, int]
MatrixData = Tuple[int, int, List[Union[ValuedMatrixEntry, VoidMatrixEntry]]]
Void = type(None)


def remove_comment(line: str) -> str:
    return line[0:line.find("%")] if line else None


def reader_header(line_iter) -> str:
    line = remove_comment(next(line_iter))
    while not line is None and len(line) == 0:
        line = remove_comment(next(line_iter))
    return line


def load_header(path: Path) -> Tuple[int, int, int]:
    with path.open('r') as file:
        line = file.readline()
        while not line is None and len(line) == 0:
            line = remove_comment(file.readline())
        n, m, nvals = line.split(' ')
        return n, m, nvals


def load(path: str) -> MatrixData:
    m = 0
    n = 0
    entries = list()

    with open(path, "r") as file:
        lines = file.readlines()
        line_iter = iter(lines)
        line = reader_header(line_iter)

        params = line.split(" ")
        assert len(params) == 3

        m, n, nvals = int(params[0]), int(params[1]), int(params[2])

        if nvals > 0:
            nvals -= 1
            line = next(line_iter)
            values = line.split(" ")
            assert len(values) == 2 or len(values) == 3

            has_values = len(values) == 3

        while line and nvals > 0:
            values = line.split(" ")
            i, j = int(values[0]), int(values[1])

            if has_values:
                assert len(values) == 3
                entries.append((i, j, int(values[2])))
            else:
                assert len(values) == 2
                entries.append((i, j))

            line = next(line_iter)
            nvals -= 1

    return m, n, entries


def save(path: str, matrix: MatrixData) -> None:
    with open(path, "w") as file:
        m, n, entries = matrix
        file.write(f"{m} {n} {len(entries)}\n")

        if len(entries) > 0:
            has_values = len(entries[0]) == 3

            if has_values:
                for i, j, v in entries:
                    file.write(f"{i} {j} {v}\n")
            else:
                for i, j in entries:
                    file.write(f"{i} {j}\n")


def value_type(matrix: MatrixData) -> Optional[MatrixValueType]:
    _, _, entries = matrix
    if entries == []:
        return None
    if len(entries[0]) < 3:
        return None
    return float if '.' in entries[0][2] else int


def has_values(matrix: MatrixData) -> bool:
    return value_type(matrix) is not None


def remove_values(matrix: MatrixData) -> str:
    assert has_values(matrix)

    m, n, entries = matrix
    result = []
    for entry in entries:
        i, j, _ = entry
        result.append((i, j))
    return (m, n, result)


def make_type_generator(t: Type) -> Callable[[], MatrixValueType]:
    if t == float:
        return random.random
    elif t == int:
        return lambda: random.randint(1, 100)
    raise Exception(f'Unable to generate type {t.name}')


def generate_values(matrix: MatrixData, generator: Callable[[], MatrixValueType]):
    assert not has_values(matrix)

    m, n, entries = matrix

    result = []
    for entry in entries:
        i, j = entry
        result.append((i, j, generator()))

    return (m, n, result)


def is_directed(mtx: MatrixData) -> bool:
    raise NotImplementedError()


def generate_directions(mtx: MatrixData) -> MatrixData:
    raise NotImplementedError()


def remove_directions(mtx: MatrixData) -> MatrixData:
    raise NotImplementedError()
