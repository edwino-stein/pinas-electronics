import typing
import configparser
from pathlib import Path

WORK_DIR: Path
CONFIG_FILE: Path
CONFIG: configparser.ConfigParser

def _set_work_dir_and_config_file(work_dir: Path, config_file: Path):
    global WORK_DIR, CONFIG_FILE
    WORK_DIR = work_dir.resolve().absolute()
    CONFIG_FILE = WORK_DIR.joinpath(config_file).resolve().absolute()

def _set_config(config: configparser.ConfigParser):
    global CONFIG
    CONFIG = config

WORK_DIR = typing.cast(Path, None)
CONFIG_FILE = typing.cast(Path, None)
CONFIG = typing.cast(configparser.ConfigParser, None)
