from enum import Enum


class ToolName(Enum):
    graphblast = 'graphblast'
    spla = 'spla'
    lagraph = 'lagraph'
    gunrock = 'gunrock'

    def __str__(self):
        return self.value
