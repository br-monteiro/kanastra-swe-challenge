from enum import Enum


class DataStatus(Enum):
    UNPROCESSED = 0
    VALID = 1
    INVALID = 2
    SKIPPED = 3
    PROCESSED = 4
