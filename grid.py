import numpy as np
from enum import IntEnum
import customtkinter as ctk
from var_config import Variables


class InitMethods(IntEnum):
    INIT_RANDOM = 0
    WARM_UP = 1


class Temperature(IntEnum):
    CONSTANT = 0
    HEATING = 1
    COOLING = 2
    SLOW_SLOW_CYCLE = 3
    SLOW_FAST_CYCLE = 4
    FAST_SLOW_CYCLE = 5


class Grid():
    def __init__(self,
                 master: ctk.CTkBaseClass):

        self.params = {
            "arr_size": master.winfo_toplevel().master_getter(Variables.LATTICE_SIZE).get(),
            "ini_cond": master.winfo_toplevel().master_getter(Variables.INIT_METHOD).get(),
            "tmp_cycl": master.winfo_toplevel().master_getter(Variables.TEMP_CYCLE).get(),
            "exc_ener": master.winfo_toplevel().master_getter(Variables.EXCHANGE_ENERGY).get(),
            "run_time": master.winfo_toplevel().master_getter(Variables.RUN_TIME).get(),
            "run_temp": master.winfo_toplevel().master_getter(Variables.TEMPERATURE).get(),
        }

        array_size = self.type_int_checker(self.params["arr_size"])
        array_size = (array_size, array_size, array_size)
        match self.params["ini_cond"]:
            case InitMethods.INIT_RANDOM:
                self.atoms = np.random.choice([-1, 1],
                                              size=array_size)
            case InitMethods.WARM_UP:
                self.atoms = np.zeros(shape=array_size,
                                      dtype=np.int8)
                self.atoms += 1
            case _:
                raise Exception

        T_min, T_max = self.temperature(self.params["run_temp"])
        self.struct_params = {
            "run_time": self.type_long_checker(self.params["run_time"]),
            "J": self.type_float_checker(self.params["exc_ener"]),
            "T_min": T_min,
            "T_max": T_max,
            "L": self.type_int_checker(self.params["arr_size"]),
            "init": self.type_int_checker(self.params["ini_cond"]),
        }

        L = self.struct_params["run:time"]
        t_min = self.struct_params["T_min"]
        t_max = self.struct_params["T_max"]

        match self.params["tmp_cycl"]:
            case Temperature.CONSTANT:
                self.temps = np.full((L,), t_min, dtype=np.float32)
            case Temperature.HEATING:
                self.temps = np.linspace(t_min, t_max, num=L)
            case Temperature.COOLING:
                self.temps = np.linspace(t_max, t_min, num=L)
            case Temperature.SLOW_SLOW_CYCLE:
                half = L // 2
                end = L - half
                temps_half = np.linspace(t_min, t_max, num=half)
                temps_end = np.linspace(t_max, t_min, num=end)
                self.temps = np.concatenate((temps_half, temps_end))
            case Temperature.SLOW_FAST_CYCLE:
                rise_len = int(L * (2/3))
                fall_len = L - rise_len
                self.temps = np.concatenate((np.linspace(t_min, t_max, num=rise_len),
                                             np.linspace(t_max, t_min, num=fall_len)))
            case Temperature.FAST_SLOW_CYCLE:
                rise_len = int(L * (1/3))
                fall_len = L - rise_len
                self.temps = np.concatenate((np.linspace(t_min, t_max, num=rise_len),
                                             np.linspace(t_max, t_min, num=fall_len)))

    def create_config_txt(self, path):
        with open(path/".config.bin", "wb") as config:
            for _, item in self.struct_params.items():
                config.write(item.tobytes())

    def export_atoms(self, path):
        bin_atoms = self.atoms.astype(np.int8)
        with open(path/".atoms.bin", "wb") as outfile:
            outfile.write(bin_atoms.tobytes())

    def export_temp_cycle(self, path):
        bin_temps = self.temps.astype(np.float32)
        with open(path/".temp_cycle.bin", "wb") as outfile:
            outfile.write(bin_temps.tobytes())

    def temperature(self, param: str):
        try:
            T_min, T_max = param.split('-')
        except Exception:
            raise Exception
        T_min = self.type_float_checker(T_min)
        T_max = self.type_float_checker(T_max)
        return T_min, T_max

    def type_int_checker(self, num):
        try:
            return np.uint32(num)
        except Exception:
            raise Exception

    def type_float_checker(self, num):
        try:
            return np.float32(num)
        except Exception:
            raise Exception

    def type_long_checker(self, num):
        try:
            return np.uint64(num)
        except Exception:
            raise Exception
