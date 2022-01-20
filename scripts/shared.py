import pathlib
import platform

ROOT = pathlib.Path(__file__).parent.parent
DATASET = ROOT / "dataset"
BUILD = ROOT / "build"

SYSTEM = {'Darwin': 'macos', 'Linux': 'linux', 'Windows': 'windows'}[platform.system()]
EXECUTABLE_EXT = {'macos': '', 'windows': '.exe', 'linux': ''}[SYSTEM]
TARGET_SUFFIX = {'macos': '.dylib', 'linux': '.so', 'windows': '.dll'}[SYSTEM]
TARGET = "spla_bench" + EXECUTABLE_EXT
