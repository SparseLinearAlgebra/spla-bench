#!/usr/bin/env python3

import argparse
from operator import concat
import sys
import urllib.request
import base64
import hashlib
import os
import tarfile
import tempfile
import shutil

import shared

from pathlib import Path

import progress


__all__ = [
    "DATASETS"
]

DATASETS = {
    '1128_bus': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/1138_bus.tar.gz',
    'abb313': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/abb313.tar.gz',
    'bcspwr03': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/bcspwr03.tar.gz',
    'soc-LiveJournal': 'https://suitesparse-collection-website.herokuapp.com/MM/SNAP/soc-LiveJournal1.tar.gz',
    'hollywood-09': 'https://suitesparse-collection-website.herokuapp.com/MM/LAW/hollywood-2009.tar.gz',
    'Journals': 'https://suitesparse-collection-website.herokuapp.com/MM/Pajek/Journals.tar.gz',
}

DATASETS_FOLDER = shared.DATASET


def parent_directory(path: str) -> str:
    parents = Path(path).resolve().parents
    if len(parents) < 1:
        raise Exception(f'Path `{path}` does not have a parent')
    return parents[0]


def file_name(path: str) -> str:
    return Path(path).resolve().name


def download_by_url(url: str, dest: str):
    if not os.path.exists(DATASETS_FOLDER):
        print(f"Creating datasets folder: '{DATASETS_FOLDER}'")
        os.makedirs(DATASETS_FOLDER)

    with tempfile.TemporaryDirectory() as temp_folder:
        archive_path = os.path.join(temp_folder, 'archive')
        archive_folder = os.path.join(temp_folder, 'unarchived')

        os.makedirs(archive_folder)

        def open_archive():
            if url.endswith('.tar.gz'):
                return tarfile.open(archive_path, "r:gz")
            elif url.endswith('.tar'):
                return tarfile.open(archive_path, "r:")
            raise Exception(f'Archive {url} is not of type \'tar\'')

        progress.download(url, archive_path)
        print(f'Archive is downloaded: {archive_path}')

        with open_archive() as unarchived_file:
            unarchived_file.extractall(archive_folder)
            print(f'Archive is opened: {archive_folder}')

        archive_contents = []
        for dirpath, dirnames, filenames in os.walk(archive_folder):
            archive_folder = dirpath
            archive_contents.extend(filenames + dirnames)

        archive_contents = list(filter(
            lambda filename: filename.endswith('.mtx'),
            archive_contents
        ))

        contents_str = archive_contents[0] if len(archive_contents) == 1 else concat(
            *map(lambda s: '\n\t- ' + s, archive_contents))

        if not archive_contents:
            raise Exception(
                f'Archive {url} does not contain .mtx file: {contents_str}')

        mtx_file = archive_contents[0]

        srcs = [mtx_file]
        dests = [dest]

        if len(archive_contents) > 1:
            dest_folder = parent_directory(dest)
            print(f'Archive contains more than two .mtx files: {contents_str}')
            print(f'They all be put in the {dest_folder}')

            srcs = []
            dests = []
            for mtx_file in archive_contents:
                srcs.append(mtx_file)
                dests.append(os.path.join(dest_folder, file_name(mtx_file)))

        assert len(srcs) == len(dests)

        for src, dst in zip(srcs, dests):
            shutil.copyfile(os.path.join(archive_folder, src), dst)
            print(f'File received: {dst}')


def get_dest_path(s: str, is_url: bool) -> str:
    file_name = f"{s}.mtx"

    if is_url:
        md5bytes = hashlib.md5(s.encode('utf-8')).digest()
        name_hash = base64.urlsafe_b64encode(md5bytes).decode('ascii')
        url_file_name = s.split('/')[-1]
        url_file_name_no_ext = url_file_name.split('.')[0]
        file_name = f"{url_file_name_no_ext}-{name_hash[:8]}.mtx"

    return os.path.join(DATASETS_FOLDER, file_name)


def download(s: str, is_url: bool, use_cached: bool):
    dest = get_dest_path(s, is_url)
    is_cached = os.path.exists(dest)

    if is_cached and use_cached:
        print(f'Dataset {s} is already downloaded: {dest}')
        return

    print(f'Downloading dataset {s} to the {dest}')
    download_by_url(s if is_url else DATASETS[s], dest)


def download_safe(s: str, is_url: bool, use_cached: bool) -> bool:
    try:
        download(s, is_url, use_cached)
        return True
    except Exception as e:
        print(
            f'An exception occured while downloading {s}: {e}', file=sys.stderr)
        return False


def main() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true',
                        default=False, help='Download all datasets')
    parser.add_argument('--name', type=str, help='Download dataset by name')
    parser.add_argument('--url', type=str, help='Download dataset by url')
    parser.add_argument('--print', action='store_true',
                        default=False, help='Print all default datasets')
    parser.add_argument('--ignore_cached', action='store_true',
                        default=False, help='Ignore cached datasets')
    args = parser.parse_args()

    if args.print:
        for name, url in DATASETS.items():
            print(f'{name}: {url}')
        sys.exit(0)

    use_cached = not args.ignore_cached

    success = True

    if args.all:
        for dataset in DATASETS.keys():
            success &= download_safe(dataset, False, use_cached)
    elif args.url:
        download(args.url, True, use_cached)
    elif args.name:
        download(args.name, False, use_cached)
    else:
        raise Exception(
            "At least one argument from 'all', 'url' or 'name' must be provided")

    print('Done!')
    return success


if __name__ == '__main__':
    main()
