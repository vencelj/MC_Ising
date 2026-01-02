from enum import IntEnum
from customtkinter import CTkBaseClass
from pathlib import Path


class Variables(IntEnum):
    APP_PATH = 1
    LOADING = 2
    INIT_METHOD = 3
    DATA_PATH = 4
    LATTICE_SIZE = 5
    TEMPERATURE = 6
    RUN_TIME = 7
    EXCHANGE_ENERGY = 8
    TEMP_CYCLE = 9


class ConfigGUI(IntEnum):
    DOC_WINDOW = 1
    LOADING_WINDOW = 2
    RESULTS_WINDOW = 3
    ERROR_WINDOW = 4

    def get_path(master: CTkBaseClass, path: str) -> Path:
        return Path(master.winfo_toplevel().master_getter(Variables.APP_PATH).get()).joinpath(path)
