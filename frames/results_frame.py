import customtkinter as ctk
import numpy as np
import struct
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from var_config import ConfigGUI
from PIL import Image
from pathlib import Path


class ResultsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master: ctk.CTkBaseClass,
                 dir_path: Path):
        super().__init__(master)

        self.dir_path = dir_path
        self._load_data()
        self.paused = True

        # animation frame
        self.animation_frame = ctk.CTkFrame(self)
        self.animation_frame.pack(side="top",
                                  padx=5,
                                  pady=5,
                                  expand=True,
                                  fill='x')

        self.play_stop_button = ctk.CTkButton(self.animation_frame,
                                              width=30,
                                              height=30,
                                              command=self._start_animation,
                                              text="Pause")
        play_stop_path = ConfigGUI.get_path(self, r"./icons/play_stop.png")
        self.play_stop_button.configure(image=ctk.CTkImage(
            light_image=Image.open(play_stop_path)))
        self.play_stop_button.pack(side="top",
                                   padx=5,
                                   pady=5,
                                   expand=True,
                                   fill='x')

        self.anim = Figure(figsize=(7, 7))
        self.anim_ax = self.anim.add_subplot(111, projection='3d')
        self.anim_ax.set_xlabel("$ L $")
        self.anim_ax.set_ylabel("$ L $")
        self.anim_ax.set_zlabel("$ L $")
        self.anim_ax.set_title("Lattice of spins")

        self.X, self.Y, self.Z = np.meshgrid(np.arange(0,
                                                       self.L, 1),
                                             np.arange(0,
                                                       self.L, 1),
                                             np.arange(0,
                                                       self.L, 1))
        self.X, self.Y, self.Z = self.X.flatten(), self.Y.flatten(), self.Z.flatten()
        self.U = np.zeros_like(self.X)
        self.V = np.zeros_like(self.Y)
        self.canvas_anim = FigureCanvasTkAgg(self.anim,
                                             self.animation_frame)
        self.canvas_anim.get_tk_widget().pack(side='top',
                                              padx=0,
                                              pady=0,
                                              fill='both',
                                              expand=True)
        self.canvas_anim.draw()
        self.toolbar_anim = NavigationToolbar2Tk(self.canvas_anim,
                                                 self.animation_frame)
        self.toolbar_anim.update()
        self.toolbar_anim.pack(side='top',
                               padx=0,
                               pady=0,
                               fill='both',
                               expand=True)

        self.slider = ctk.CTkSlider(self.animation_frame,
                                    from_=0,
                                    to=self.atoms.shape[0],
                                    state="disabled")
        self.slider.set(0)
        self.slider.pack(side='top',
                         padx=0,
                         pady=0,
                         fill='x',
                         expand=True)

        self.ani = FuncAnimation(self.anim, self._animation, frames=self.atoms.shape[0],
                                 interval=500, cache_frame_data=False)
        self.ani.pause()

        # graph frame
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(side="top",
                              padx=5,
                              pady=5,
                              expand=True,
                              fill='x')

        self.temp_graph = Figure(figsize=(7, 7))
        self.temp_ax = self.temp_graph.add_subplot(111)
        self.temp_ax.set_xlabel("$ i $")
        self.temp_ax.set_ylabel("$ T $", color="blue")
        self.temp_ax.plot(self.iterations,
                          self.temp_cycle,
                          color="blue")
        self.temp_ax.axvline(x=0, color='k')
        self.temp_ax.axhline(y=0, color='k')
        self.temp_ax.set_title("Net Energy $E$")
        self.temp_canvas = FigureCanvasTkAgg(self.temp_graph,
                                             self.graph_frame)
        self.temp_canvas.get_tk_widget().pack(side='top',
                                              padx=0,
                                              pady=0,
                                              fill='both',
                                              expand=True)
        self.toolbar_temp = NavigationToolbar2Tk(self.temp_canvas,
                                                 self.graph_frame)
        self.toolbar_temp.update()
        self.toolbar_temp.pack(side='top',
                               padx=0,
                               pady=0,
                               fill='both',
                               expand=True)

        self.energy_graph = Figure(figsize=(7, 7))
        self.energy_ax = self.energy_graph.add_subplot(111)
        self.energy_ax.set_xlabel("$ T $")
        self.energy_ax.set_ylabel("$ E $", color="blue")
        self.energy_ax.plot(self.iterations,
                            self.energy,
                            color="blue")
        self.energy_ax.axvline(x=0, color='k')
        self.energy_ax.axhline(y=0, color='k')
        self.energy_ax.set_title("Net Energy $E$")
        self.energy_canvas = FigureCanvasTkAgg(self.energy_graph,
                                               self.graph_frame)
        self.energy_canvas.get_tk_widget().pack(side='top',
                                                padx=0,
                                                pady=0,
                                                fill='both',
                                                expand=True)
        self.toolbar_energy = NavigationToolbar2Tk(self.energy_canvas,
                                                   self.graph_frame)
        self.toolbar_energy.update()
        self.toolbar_energy.pack(side='top',
                                 padx=0,
                                 pady=0,
                                 fill='both',
                                 expand=True)

        self.magnetization_graph = Figure(figsize=(7, 7))
        self.magnetization_ax = self.magnetization_graph.add_subplot(111)
        self.magnetization_ax.set_xlabel("$ T $")
        self.magnetization_ax.set_ylabel("$ M $", color="blue")
        self.magnetization_ax.plot(self.iterations,
                                   self.magnetization,
                                   color="blue")
        self.magnetization_ax.axvline(x=0, color='k')
        self.magnetization_ax.axhline(y=0, color='k')
        self.magnetization_ax.set_title("Net Energy $E$")
        self.magnetization_canvas = FigureCanvasTkAgg(self.magnetization_graph,
                                                      self.graph_frame)
        self.magnetization_canvas.get_tk_widget().pack(side='top',
                                                       padx=0,
                                                       pady=0,
                                                       fill='both',
                                                       expand=True)
        self.toolbar_magnetization = NavigationToolbar2Tk(self.magnetization_canvas,
                                                          self.graph_frame)
        self.toolbar_magnetization.update()
        self.toolbar_magnetization.pack(side='top',
                                        padx=0,
                                        pady=0,
                                        fill='both',
                                        expand=True)

    def _start_animation(self, *_):
        if self.paused:
            self.ani.resume()
            self.paused = False
            self.play_stop_button.configure(text="Pause")
        else:
            self.ani.pause()
            self.paused = True
            self.play_stop_button.configure(text="Play")

    def _animation(self, frame_idx, *_):
        self.slider.set(frame_idx)
        self.anim_ax.clear()
        W = self.atoms[frame_idx].flatten()
        colors = np.where(W > 0, 'red', 'blue')
        self.anim_ax.quiver(self.X, self.Y, self.Z,
                            self.U, self.V, W,
                            colors=colors, length=0.6, normalize=True)
        self.anim_ax.set_title(f"Lattice Spin - Step {frame_idx}")
        self.anim_ax.set_xlim(0, self.L)
        self.anim_ax.set_ylim(0, self.L)
        self.anim_ax.set_zlim(0, self.L)
        self.canvas_anim.draw_idle()

    def _load_data(self):
        with open(self.dir_path/".config.bin", "rb") as f:
            config = f.read()
        params = struct.unpack("Qfffii", config)
        self.grid_configuration = {
            "run_time": params[0],
            "J": params[1],
            "T_min": params[2],
            "T_max": params[3],
            "L": params[4],
        }
        self.L = self.grid_configuration["L"]

        self.temp_cycle = np.fromfile(self.dir_path/".temp_cycle.bin",
                                      dtype=np.float32)

        raw_atoms = np.fromfile(self.dir_path/".atoms.bin",
                                dtype=np.int8)
        self.atoms = raw_atoms.reshape((-1,
                                        self.grid_configuration["L"],
                                        self.grid_configuration["L"],
                                        self.grid_configuration["L"]))

        raw_meas = np.fromfile(self.dir_path/".measurment.bin",
                               dtype=np.int8)
        raw_meas = raw_meas.reshape(-1, 2)
        self.magnetization = raw_meas[:, 0]
        self.energy = raw_meas[:, 1]

        self.iterations = np.arange(len(self.magnetization))
