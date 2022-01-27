import urllib.request
import sys
import pathlib


DEFAULT_DOWNLOAD_CHUNK_SIZE = 4096


class Download:
    def __init__(self, url, dest):
        self.request = urllib.request.urlopen(url)
        self.url = url
        content_length = self.request.headers['content-length']
        self.file_size = None if content_length is None else int(
            content_length)
        self.downloaded = 0
        self.dest_filename = dest
        self.dest_stream = None
        self.request_body_stream = None

    def __len__(self):
        if self.file_size is None:
            raise Exception(
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
    except AttributeError:
        return None


class Progress:
    def __init__(self,
                 context_manager,
                 name='Process',
                 chunk: int = DEFAULT_DOWNLOAD_CHUNK_SIZE,
                 total: int = None,
                 out=sys.stdout):
        self.context_manager = context_manager
        self.name = name
        self.chunk = chunk
        self.out = out
        self.total = try_extract_len(
            context_manager) if total is None else total
        self.progress = 0
        self.bar_length = 20
        self.prev_progress_string = None

    def __iter__(self):
        self.context_manager.__enter__()
        return self

    def __print(self, s: str):
        if self.out is not None:
            print(s, file=self.out, end='')

    def __reset_line(self):
        self.__print('\r')

    def __format_progress(self) -> str:
        status = None
        part = None
        if self.total is None:
            part = 0.0
            status = f'{self.progress} / ?'
        elif self.progress == 0:
            part = 0.0
            status = 'initializing'
        elif self.progress == self.total:
            part = 1.0
            status = 'done!       \n'
        else:
            part = self.progress / self.total
            status = '{:.1%}'.format(self.progress / self.total)
            if part < 0.1:
                status = ' ' + status
            status += ' ' * 7
        empty_bars = int(self.bar_length * (1.0 - part))
        filled_bars = self.bar_length - empty_bars
        filled = '=' * filled_bars
        empty = ' ' * empty_bars
        arrow = '>' if part < 1.0 else '='
        return f'{self.name}: [{filled}{arrow}{empty}] {status}'

    def __next__(self):
        data = self.context_manager.read(self.chunk)
        if data is None or len(data) == 0:
            raise StopIteration()
        self.progress += len(data)
        if self.out is not None:
            progress_string = self.__format_progress()
            if progress_string != self.prev_progress_string:
                self.__reset_line()
                self.__print(progress_string)
                self.prev_progress_string = progress_string
        return data


def download(url: str, dest: str, chunk=DEFAULT_DOWNLOAD_CHUNK_SIZE, mute: bool = False):
    filename = pathlib.Path(url).name
    process_name = f'Downloading {filename}'
    out = None if mute else sys.stdout
    for _ in Progress(Download(url, dest), process_name, chunk, None, out):
        pass
