from enum import Enum


class NodeStatus(Enum):
    NEW = 1
    STARTING = 2
    STARTED = 3
    KILLING = 4
    KILLED = 5
    DISABLED = 6
