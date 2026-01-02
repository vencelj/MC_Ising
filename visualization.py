import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from frames import *
from var_config import Variables, ConfigGUI
from pathlib import Path
import platform
from grid import InitMethods, Temperature


class Simulant(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.variables = {
            Variables.APP_PATH: ctk.StringVar(self,
                                              str(Path(__file__).resolve().parent)),
            Variables.LOADING: ctk.IntVar(self,
                                          0),
            Variables.INIT_METHOD: ctk.IntVar(self, InitMethods.WARM_UP),
            Variables.TEMP_CYCLE: ctk.IntVar(self, Temperature.CONSTANT),
            Variables.TEMPERATURE: ctk.StringVar(self, "1.5-2.8"),
            Variables.EXCHANGE_ENERGY: ctk.StringVar(self, "1"),
            Variables.LATTICE_SIZE: ctk.StringVar(self, "40"),
            Variables.RUN_TIME: ctk.StringVar(self, "1024"),
            Variables.DATA_PATH: ctk.StringVar(self,
                                               str(Path(__file__).resolve().parent)),
        }

        self.title("Monte Carlo simulation – Ising model")
        self.geometry("512x512")
        self.resizable(width=False, height=False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        if platform.system() == "Windows":
            self.iconbitmap(ConfigGUI.get_path(self,
                                               r"./icons/app_icon.ico"))

        MainFrame(self).pack(side="top",
                             padx=0,
                             pady=0,
                             expand=True,
                             fill="both")

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.get_path)

        self.bind_all("<Control-w>", self._self_destroy)

    def _self_destroy(self, *_):
        self.destroy()

    def master_getter(self, var: Variables):
        return self.variables[var]

    def master_setter(self, var: Variables, val):
        self.variables[var].set(val)

    def get_path(self, event):
        self.variables[Variables.DATA_PATH].set(
            Path(event.data.replace("{", "").replace("}", "")))

    def window_mannager(self, window: ConfigGUI, load=True, message="", dir_path: Path = None):
        match window:
            case ConfigGUI.RESULTS_WINDOW:
                win = WindowBuilder(master=self,
                                    title="Results",
                                    geometry="1400x700")
                ResultsFrame(win, dir_path).pack(side="top",
                                                 padx=0,
                                                 pady=0,
                                                 expand=True,
                                                 fill="both")
            case ConfigGUI.ERROR_WINDOW:
                self.error_screen = WindowBuilder(master=self,
                                                  title="Error",
                                                  geometry="350x100",
                                                  resizable=False,
                                                  disable_closing=False,
                                                  top_most=True)
                ErrorFrame(self.error_screen, message).pack(side="top",
                                                            padx=0,
                                                            pady=0,
                                                            expand=True,
                                                            fill="both")
            case ConfigGUI.LOADING_WINDOW:
                if load:
                    self.loading_screen = WindowBuilder(master=self,
                                                        title="Loading...",
                                                        geometry="300x100",
                                                        resizable=False,
                                                        disable_closing=True,
                                                        top_most=True)
                    LoadingFrame(self.loading_screen).pack(side="top",
                                                           padx=0,
                                                           pady=0,
                                                           expand=True,
                                                           fill="both")
                    self.config(cursor="clock")
                else:
                    self.loading_screen.destroy()
                    self.config(cursor="arrow")
