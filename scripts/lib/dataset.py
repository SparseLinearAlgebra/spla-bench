from dataclasses import dataclass
import os
import tempfile
import shutil
import json

from enum import Enum
from pathlib import Path
from operator import concat
from typing import List, Any, Optional, Type, Callable

import config
import lib.progress as progress
import lib.util as util
import lib.matrix as matrix


def download_by_url(url: str, dest: Path):
    if not os.path.exists(config.DATASET_FOLDER):
        print(f"Creating datasets folder: '{config.DATASET_FOLDER}'")
        os.makedirs(config.DATASET_FOLDER)

    with tempfile.TemporaryDirectory() as temp_folder_name:
        temp_folder = Path(temp_folder_name)

        archive_path = temp_folder / 'archive'
        archive_folder = temp_folder / 'unarchived'

        os.makedirs(archive_folder)

        progress.download(url, archive_path)
        progress.unarchive(archive_path, archive_folder)

        archive_contents: List[Path] = []
        for dirpath, dirnames, filenames in os.walk(archive_folder):
            archive_folder = dirpath
            archive_contents.extend(map(Path, filenames + dirnames))

        archive_contents = list(filter(
            lambda filename: filename.endswith('.mtx'),
            archive_contents
        ))

        contents_str = archive_contents[0] if len(archive_contents) == 1 else concat(
            *map(lambda s: '\n\t- ' + s, archive_contents)
        )

        if not archive_contents:
            raise Exception(
                f'Archive {url} does not contain .mtx file: {contents_str}')

        mtx_file = archive_contents[0]

        srcs = [mtx_file]
        dests = [dest]

        if len(archive_contents) > 1:
            dest_folder = util.parent_directory(dest)
            print(f'Archive contains more than two .mtx files: {contents_str}')
            print(f'They all be put in the {dest_folder}')

            srcs = []
            dests = []
            for mtx_file in archive_contents:
                srcs.append(mtx_file)
                dests.append(os.path.join(
                    dest_folder, util.file_name(mtx_file)))

        assert len(srcs) == len(dests)

        for src, dst in zip(srcs, dests):
            shutil.copyfile(os.path.join(archive_folder, src), dst)
            print(f'File received: {dst}')


class DatasetPropertiesCache:
    def set(dataset_name: str, key: Any, value: Any):
        raise NotImplementedError()

    def get(dataset_name: str, key: Any, type: Type) -> Any:
        raise NotImplementedError()

    def get_or_eval(dataset_name: str, key: Any, get_value: Callable, type: Type) -> Any:
        cached_value = DatasetPropertiesCache.get(dataset_name, key, type)
        if cached_value is not None:
            return cached_value
        value = get_value()
        DatasetPropertiesCache.set(dataset_name, key, value)
        return value


def make_dest_path(name: str) -> Path:
    file_name = f'{name}.mtx'
    return config.DATASET_FOLDER / file_name


def download(name: str) -> Path:
    dest = make_dest_path(name)
    if dest.exists():
        return
    if config.DATASET_URL[name] is None:
        raise Exception(f'Url to the dataset {name} is not set')
    download_by_url(config.DATASET_URL[name], dest)
    if not dest.exists():
        raise Exception(f'Can not download dataset {name}')
    return dest


def get_dataset(name: str) -> Path:
    dataset_local_path = make_dest_path(name)

    has_cached = DatasetPropertiesCache.get(name, 'path', Path) is not None
    has_url = name in config.DATASET_URL
    is_downloaded = dataset_local_path.exists()

    if not any([has_cached, has_url, is_downloaded]):
        raise Exception(
            f'Dataset {name} is not cached, does not have url nor downloaded')

    def get_dataset_named():
        if has_url and not is_downloaded:
            download(name)
        return dataset_local_path

    return DatasetPropertiesCache.get_or_eval(name, 'path', get_dataset_named, Path)


class DatasetValueType(Enum):
    float = (float, 'float')
    void = (type(None), 'void')
    int = (int, 'int')

    def to_type(self) -> Type:
        return self.value[0]

    def __str__(self) -> str:
        return self.value[1]


def dataset_type_from_type(python_type: Type) -> DatasetValueType:
    if python_type is None:
        return DatasetValueType.void
    for dataset_type in list(DatasetValueType):
        if python_type == dataset_type.to_type():
            return dataset_type
    raise Exception(f'Can not build dataset type from {python_type}')


def dataset_type_from_repr(type_name: str) -> DatasetValueType:
    assert type_name is not None
    for dataset_type in list(DatasetValueType):
        if type_name == str(dataset_type):
            return dataset_type
    raise Exception(f'Can not build dataset type from {type_name}')


@dataclass
class DatasetProperties:
    directed: Optional[bool]
    element_type: Optional[DatasetValueType]


class Dataset:
    def __init__(self, name: str):
        self.name = name
        self.path = get_dataset(name)

    def get_directed(self) -> bool:
        def calculate_directed():
            matrix_data = matrix.load(self.path)
            return matrix.is_directed(matrix_data)
        return DatasetPropertiesCache.get_or_eval(
            self.name,
            'directed',
            calculate_directed,
            bool)

    def get_element_type(self) -> DatasetValueType:
        def calculate_type():
            matrix_data = matrix.load(self.path)
            return dataset_type_from_type(matrix.value_type(matrix_data))
        return DatasetPropertiesCache.get_or_eval(
            self.name,
            'element_type',
            calculate_type,
            DatasetValueType)

    def get_properties(self) -> DatasetProperties:
        return DatasetProperties(
            directed=self.get_directed(),
            element_type=self.get_element_type())

    def get_edges(self) -> int:
        _, _, nvals = matrix.load_header(self.path)
        return nvals

    def get_category(self) -> config.DatasetSize:
        return config.DatasetSize.from_n_edges(self.get_edges())
