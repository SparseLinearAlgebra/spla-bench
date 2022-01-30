import os
import subprocess

from enum import Enum
from pathlib import Path
from typing import Tuple, List

import config
import lib.progress as progress

from lib.util import check_paths_exist


