import abc
import urllib.request
import sys
import tarfile
import os
import io

from pathlib import Path
from typing import Optional, Any


DEFAULT_CHUNK_SIZE = 4096
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}


class Download:
    def __init__(self, url: str, dest: Path):
        download_request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        self.request = urllib.request.urlopen(download_request)
        self.url = url
        content_length = self.request.headers.get('content-length', None)
        self.file_size = None if content_length is None else int(
            content_length)
        self.downloaded = 0
        self.dest_filename = dest
        self.dest_stream = None
        self.request_body_stream = None

    def __len__(self):
        if self.file_size is None:
            raise KeyError(
                'Cannot tell exact downloaded file size. `content-length` header is empty')
        return self.file_size

    def __enter__(self):
        self.request_body_stream = self.request.__enter__()
        self.dest_stream = open(self.dest_filename, 'wb')
        return self

    def read(self, nbytes: int = None):
        if self.downloaded == self.file_size:
            return None
        if self.request_body_stream is None:
            self.__enter__()
        data: bytes = None
        if nbytes is None:
            data = self.request_body_stream.read()
        else:
            data = self.request_body_stream.read(nbytes)
        self.downloaded += len(data)
        self.dest_stream.write(data)
        return data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dest_stream is None:
            raise Exception('Download was already stopped')
        self.dest_stream.__exit__()
        self.request_body_stream.__exit__()
        self.dest_stream = None
        self.request_body_stream = None

    def close(self):
        if self.dest_stream is not None:
            self.__exit__()


def try_extract_len(a):
    try:
        return len(a)
    except (AttributeError, KeyError):
        return None


class ProgressFormatter:
    def __init__(self):
        self.prev_progress_string = None

    @abc.abstractmethod
    def total_size(self) -> int:
        pass

    @abc.abstractmethod
    def progress(self) -> int:
        pass

    @abc.abstractmethod
    def process_name(self) -> str:
        pass

    @abc.abstractmethod
    def output_stream(self) -> Optional[Any]:
        return sys.stdout

    def __print(self, s: str):
        if self.output_stream() is not None:
            print(s, file=self.output_stream(), end='')

    def __reset_line(self):
        self.__print('\r')

    def __format_progress(self) -> str:
        status = None
        part = None
        if self.total_size() is None:
            part = 0.0
            status = f'{self.progress()} / ?'
        elif self.progress() == 0:
            part = 0.0
            status = 'initializing'
        elif self.progress() == self.total_size():
            part = 1.0
            status = 'done!       \n'
        else:
            part = self.progress() / self.total_size()
            status = '{:.1%}'.format(self.progress() / self.total_size())
            if part < 0.1:
                status = ' ' + status
            status += ' ' * 7
        bar_length = 20
        empty_bars = int(bar_length * (1.0 - part))
        filled_bars = bar_length - empty_bars
        filled = '=' * filled_bars
        empty = ' ' * empty_bars
        arrow = '>' if part < 1.0 else '='
        return f'{self.process_name()}: [{filled}{arrow}{empty}] {status}'

    def print_progress(self):
        if self.output_stream() is None:
            return
        progress_string = self.__format_progress()
        if progress_string != self.prev_progress_string:
            self.__reset_line()
            self.__print(progress_string)
            self.prev_progress_string = progress_string


class ReadProgress(ProgressFormatter):
    def __init__(self,
                 context_manager,
                 name='Process',
                 chunk: int = DEFAULT_CHUNK_SIZE,
                 total: int = None,
                 out=sys.stdout):
        ProgressFormatter.__init__(self)
        self.context_manager = context_manager
        self.p_name = name
        self.chunk = chunk
        self.out = out
        self.total = try_extract_len(
            context_manager) if total is None else total
        self.total_read = 0

    def process_name(self) -> str:
        return self.p_name

    def total_size(self) -> int:
        return self.total

    def progress(self) -> int:
        return self.total_read

    def output_stream(self) -> Optional[Any]:
        return self.out

    def __iter__(self):
        self.context_manager.__enter__()
        return self

    def __next__(self):
        data = self.context_manager.read(self.chunk)
        if data is None or len(data) == 0:
            raise StopIteration()
        self.total_read += len(data)
        self.print_progress()


def download(url: str, dest: Path, chunk=DEFAULT_CHUNK_SIZE, mute: bool = False):
    filename = Path(url).name
    process_name = f'Downloading {filename}'
    out = None if mute else sys.stdout
    for _ in ReadProgress(Download(url, dest), process_name, chunk, None, out):
        pass


class ProgressFileObject(io.FileIO, ProgressFormatter):
    def __init__(self, path, *args, **kwargs):
        ProgressFormatter.__init__(self)
        self._total_size = os.path.getsize(path)
        self._archive_name = ''
        io.FileIO.__init__(self, path, *args, **kwargs)

    def process_name(self) -> str:
        return f'Unarchiving {self._archive_name}'

    def total_size(self) -> int:
        return self._total_size

    def progress(self) -> int:
        return self.tell()

    def read(self, size):
        self.print_progress()
        return io.FileIO.read(self, size)


def unarchive(source: Path, dest: Path):
    with tarfile.open(fileobj=ProgressFileObject(source)) as tar:
        tar.extractall(dest)
