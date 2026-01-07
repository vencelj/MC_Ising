import customtkinter as ctk
from tkinter.filedialog import askdirectory
from tkinterdnd2 import TkinterDnD, DND_FILES
from CTkMenuBar import *
from PIL import Image, ImageTk
from pathlib import Path
import webbrowser
from var_config import ConfigGUI, Variables
from processing_mannager import generate_protocol


class MainFrame(ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self,
                 master: ctk.CTkBaseClass):
        super().__init__(master)

        self.master = master
        self.init_values = ["Random", "Warm-Up"]
        self.cycle_values = ["Constant", "Heating", "Cooling", "Slow Heating – Slow Cooling",
                             "Slow Heating – Fast Cooling", "Fast Heating – Slow Cooling"]

        self.data_path: ctk.StringVar = self.master.winfo_toplevel(
        ).master_getter(Variables.DATA_PATH)
        self.data_path.trace_add("write", self._update_path_label)

        self.run_time: ctk.IntVar = self.master.winfo_toplevel(
        ).master_getter(Variables.RUN_TIME)
        self.exchange_energy: ctk.StringVar = self.master.winfo_toplevel(
        ).master_getter(Variables.EXCHANGE_ENERGY)
        self.temperature: ctk.StringVar = self.master.winfo_toplevel(
        ).master_getter(Variables.TEMPERATURE)
        self.lattice_size: ctk.IntVar = self.master.winfo_toplevel(
        ).master_getter(Variables.LATTICE_SIZE)
        self.init_method: ctk.IntVar = self.master.winfo_toplevel(
        ).master_getter(Variables.INIT_METHOD)
        self.temp_cycle: ctk.IntVar = self.master.winfo_toplevel(
        ).master_getter(Variables.TEMP_CYCLE)

        # tool bar
        menu = CTkMenuBar(self)

        file_button = menu.add_cascade("Simulation")
        about_button = menu.add_cascade("About",
                                        postcommand=self._open_documentation)

        dropdown_file = CustomDropdownMenu(widget=file_button)
        dropdown_file.add_option(option="New simulation",
                                 command=self.start_simulation)
        dropdown_file.add_option(option="Open data",
                                 command=self._open_new)

        # create background image
        self.bg_im_path = ConfigGUI.get_path(self,
                                             r"./icons/background_image.png")
        self.bg_im = Image.open(self.bg_im_path)
        self.bg_im = ImageTk.PhotoImage(self.bg_im)

        # canvas
        self.canvas = ctk.CTkCanvas(self,
                                    width=self.master.winfo_width(),
                                    height=self.master.winfo_height(),
                                    bd=0,
                                    highlightthickness=0)
        self.canvas.pack(side="top",
                         padx=0,
                         pady=0,
                         fill="both",
                         expand=True)
        self.canvas.create_image(0, 0, image=self.bg_im, anchor='nw')

        # drag & drop
        self.label_path = ctk.CTkLabel(self,
                                       text="Drag & Drop\nor\nOpen New",
                                       bg_color="#f0f0f0")
        self.selected_path = ctk.CTkLabel(self,
                                          text="",
                                          bg_color="#f0f0f0")

        self.canvas.create_window(20,
                                  20,
                                  anchor="nw",
                                  window=self.label_path)
        self.canvas.create_window(20,
                                  80,
                                  anchor="nw",
                                  window=self.selected_path)

        # simulation setting
        self.exchange_energy_label = ctk.CTkLabel(self,
                                                  text="Exchange energy J (eV):",
                                                  bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  120,
                                  anchor="nw",
                                  window=self.exchange_energy_label)
        self.exchange_energy_entry = ctk.CTkEntry(self,
                                                  textvariable=self.exchange_energy,
                                                  bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  150,
                                  anchor="nw",
                                  window=self.exchange_energy_entry)

        self.lattice_label = ctk.CTkLabel(self,
                                          text="Lattice size (1-255):",
                                          bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  200,
                                  anchor="nw",
                                  window=self.lattice_label)
        self.lattice_size_entry = ctk.CTkEntry(self,
                                               textvariable=self.lattice_size,
                                               bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  230,
                                  anchor="nw",
                                  window=self.lattice_size_entry)

        self.temp_label = ctk.CTkLabel(self,
                                       text="Tempature (min-max):",
                                       bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  280,
                                  anchor="nw",
                                  window=self.temp_label)
        self.temperature_entry = ctk.CTkEntry(self,
                                              textvariable=self.temperature,
                                              bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  310,
                                  anchor="nw",
                                  window=self.temperature_entry)

        self.time_label = ctk.CTkLabel(self,
                                       text="Run Time (iterations):",
                                       bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  360,
                                  anchor="nw",
                                  window=self.time_label)
        self.run_time_entry = ctk.CTkEntry(self,
                                           textvariable=self.run_time,
                                           bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  390,
                                  anchor="nw",
                                  window=self.run_time_entry)

        self.init_method_label = ctk.CTkLabel(self,
                                              text="Initial condition:",
                                              bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  440,
                                  anchor="nw",
                                  window=self.init_method_label)
        self.init_method_combo = ctk.CTkComboBox(self,
                                                 values=self.init_values,
                                                 bg_color="#f0f0f0")
        self.init_method_combo.set(self.init_values[self.init_method.get()])
        self.canvas.create_window(20,
                                  470,
                                  anchor="nw",
                                  window=self.init_method_combo)

        self.temp_cycle_label = ctk.CTkLabel(self,
                                             text="Temperature cycle:",
                                             bg_color="#f0f0f0")
        self.canvas.create_window(20,
                                  520,
                                  anchor="nw",
                                  window=self.temp_cycle_label)
        self.temp_cycle_combo = ctk.CTkComboBox(self,
                                                values=self.cycle_values,
                                                bg_color="#f0f0f0")
        self.temp_cycle_combo.set(self.cycle_values[self.temp_cycle.get()])
        self.canvas.create_window(20,
                                  550,
                                  anchor="nw",
                                  window=self.temp_cycle_combo)

        self.processing_button = ctk.CTkButton(self,
                                               text="Start Simulation",
                                               command=self.start_simulation,
                                               bg_color="#f0f0f0")
        button_im_path = ConfigGUI.get_path(self, r"./icons/protocol.png")
        self.processing_button.configure(image=ctk.CTkImage(light_image=Image.open(button_im_path)),
                                         compound="left")
        self.canvas.create_window(350,
                                  512,
                                  anchor="nw",
                                  window=self.processing_button)

        # binding
        self.master.bind_all("<Control-o>", self._open_new)
        self.master.bind_all("<Control-p>", self.start_simulation)

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.delegate_path)

    def _open_documentation(self, *_):
        doc_path = ConfigGUI.get_path(self,
                                      r"./protocol/protokol_vencelj.pdf")
        webbrowser.open_new(f"file://{doc_path}")

    def _open_new(self, *_):
        if self.master.winfo_toplevel().master_getter(Variables.DATA_PATH).get() \
                == self.master.winfo_toplevel().master_getter(Variables.APP_PATH).get():
            init_dir = Path.home()
        else:
            init_dir = Path(self.master.winfo_toplevel().master_getter(
                Variables.DATA_PATH).get()).parents[0]

        im_path = askdirectory(initialdir=init_dir,
                               title="Select datafile",
                               mustexist=True)
        if im_path:
            self.master.winfo_toplevel().master_setter(Variables.DATA_PATH, str(im_path))

        generate_protocol(master=self)

    def _update_path_label(self, *_):
        data_path = Path(self.master.winfo_toplevel(
        ).master_getter(Variables.DATA_PATH).get())
        app_path = Path(self.master.winfo_toplevel(
        ).master_getter(Variables.APP_PATH).get())
        if data_path != app_path:
            self.selected_path.configure(text=data_path.name)

    def start_simulation(self, *_):
        self.master.winfo_toplevel().master_setter(Variables.INIT_METHOD,
                                                   self.init_values.index(self.init_method_combo.get()))
        self.master.winfo_toplevel().master_setter(Variables.TEMP_CYCLE,
                                                   self.cycle_values.index(self.temp_cycle_combo.get()))
        generate_protocol(master=self)

    def delegate_path(self, event):
        self.master.get_path(event)
