import customtkinter as ctk
from PIL import Image
from var_config import ConfigGUI


class ErrorFrame(ctk.CTkFrame):
    def __init__(self, master, error_message):
        super().__init__(master)

        ctk.CTkLabel(self,
                     text="",
                     image=ctk.CTkImage(light_image=Image.open(ConfigGUI.get_path(master,
                                                                                  r"./icons/error.png")))).pack(side="left",
                                                                                                                padx=5,
                                                                                                                pady=5,
                                                                                                                expand=True,
                                                                                                                fill="both")
        ctk.CTkLabel(self,
                     text=error_message,
                     anchor="w").pack(side="left",
                                      padx=5,
                                      pady=5)
