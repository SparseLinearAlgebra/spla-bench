import shared

__all__ = [
    "load",
    "save"
]


def remove_comment(line: str):
    return line[0:line.find("%")] if line else None


def reader_header(line_iter):
    line = remove_comment(next(line_iter))
    while not line is None and len(line) == 0:
        line = remove_comment(next(line_iter))
    return line


def load(path):
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


def save(path, matrix):
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
