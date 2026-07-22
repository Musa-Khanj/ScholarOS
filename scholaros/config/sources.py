from enum import Enum


class ConfigSource(str, Enum):
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    COMMAND_LINE = "command-line"