import customtkinter as ctk
from var_config import ConfigGUI
import platform


class WindowBuilder(ctk.CTkToplevel):
    def __init__(self,
                 master: ctk.CTkBaseClass,
                 title: str,
                 geometry: str,
                 resizable: bool = True,
                 disable_closing: bool = False,
                 top_most: bool = False):
        super().__init__(master)
        self.master = master

        self.title(title)
        self.geometry(geometry)
        if platform.system() == "Windows":
            self.after(200, lambda: self.iconbitmap(ConfigGUI.get_path(self,
                                                                       r"./icons/app_icon.ico")))

        self.resizable(width=resizable,
                       height=resizable)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        if disable_closing:
            self.protocol("WM_DELETE_WINDOW", self._disable_closing)

        if top_most:
            self.attributes("-topmost", "true")

    def _disable_closing(self, *_):
        pass

    def master_getter(self, var):
        return self.master.winfo_toplevel().variables[var]

    def master_setter(self, var, val):
        self.master.winfo_toplevel().variables[var].set(val)

    def calibration(self, load: bool):
        self.master.winfo_toplevel().calibration(load)
