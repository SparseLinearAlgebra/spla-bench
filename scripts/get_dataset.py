import argparse
from ctypes import ArgumentError
import sys
import urllib.request
import base64
import hashlib
import os
import tarfile
import tempfile
import shutil

from typing import List


DATASETS = {
    '1128_bus': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/1138_bus.tar.gz',
    'abb313': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/abb313.tar.gz',
    'bcspwr03': 'https://suitesparse-collection-website.herokuapp.com/MM/HB/bcspwr03.tar.gz'
}

DATASETS_FOLDER = 'datasets'


def download_by_url(url: str, dest: str = None):
    if not os.path.exists(DATASETS_FOLDER):
        print(f"Creating datasets folder: '{DATASETS_FOLDER}'")
        os.makedirs(DATASETS_FOLDER)

    with tempfile.TemporaryDirectory() as temp_folder:
        arhive_path = os.path.join(temp_folder, 'archive')
        archive_folder = os.path.join(temp_folder, 'unarchived')

        os.makedirs(archive_folder)

        def open_archive():
            if url.endswith('.tar.gz'):
                return tarfile.open(arhive_path, "r:gz")
            elif url.endswith('.tar'):
                return tarfile.open(arhive_path, "r:")
            raise ArgumentError(f'Archive {url} is not of type \'tar\'')

        with urllib.request.urlopen(url) as url_file:
            content = url_file.read()
            with open(arhive_path, 'wb') as dest_file:
                dest_file.write(content)
                print(f'Archive is downloaded: {arhive_path}')

        with open_archive() as unarchived_file:
            unarchived_file.extractall(archive_folder)
            print(f'Archive is opened: {archive_folder}')

        archive_contents = []
        for dirpath, dirnames, filenames in os.walk(archive_folder):
            archive_contents.extend(
                list(map(lambda d: os.path.join(dirpath, d), filenames + dirnames)))
        archive_contents = list(
            filter(lambda filename: filename.endswith('.mtx'), archive_contents))
        contents_str = ', '.join(archive_contents)

        if archive_contents == []:
            raise Exception(
                f'Archive {url} does not contain .mtx file: {contents_str}')
        if len(archive_contents) > 1:
            raise Exception(
                f'Archive {url} contains more than two .mtx files: {contents_str}')

        mtx_file = f'{archive_contents[0]}'
        shutil.copyfile(src=mtx_file, dst=dest)


def get_dest_path(s: str, is_url: bool) -> str:
    file_name = s

    if is_url:
        md5bytes = hashlib.md5(s.encode('utf-8')).digest()
        hash = base64.urlsafe_b64encode(md5bytes).decode('ascii')
        url_file_name = s.split('/')[-1]
        url_file_name_no_ext = url_file_name.split('.')[0]

        file_name = f'{url_file_name_no_ext}-{hash[:8]}'

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


def main(arg_strings: List[str]) -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true',
                        default=False, help='Download all datasets')
    parser.add_argument('--name', type=str, help='Download dataset by name')
    parser.add_argument('--url', type=str, help='Download dataset by url')
    parser.add_argument('--print', action='store_true',
                        default=False, help='Print all default datasets')
    parser.add_argument('--ignore_cached', action='store_true',
                        default=False, help='Ignore cached datasets')
    args = parser.parse_args(arg_strings)

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
        raise ArgumentError(
            "At least one argument from 'all', 'url' or 'name' must be provided")

    return success


if __name__ == '__main__':
    try:
        if main(sys.argv[1:]):
            print('Done!')
        else:
            raise('Download was not successful')
    except Exception as e:
        print(f'{type(e).__name__}: {e}', file=sys.stderr)
