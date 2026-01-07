import customtkinter as ctk
import numpy as np
import struct
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from var_config import ConfigGUI
from PIL import Image
from pathlib import Path
from threading import Thread


plt.rcParams.update({
"text.usetex": True,
"font.family": "serif",
"font.serif": ["Computer Modern Roman"],
"text.latex.preamble": r'\usepackage{siunitx}',
})


class ResultsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master: ctk.CTkBaseClass,
                 dir_path: Path):
        super().__init__(master)

        self.dir_path = dir_path
        self._load_data()
        self.paused = True

        # animation frame
        self.animation_frame = ctk.CTkFrame(self,
                                            height=1200)
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
        play_stop_path = ConfigGUI.get_path(self, r"./icons/play_pause.png")
        self.play_stop_button.configure(image=ctk.CTkImage(
            light_image=Image.open(play_stop_path)))
        self.play_stop_button.pack(side="top",
                                   padx=5,
                                   pady=5,
                                   expand=False)

        self.anim = Figure(figsize=(9, 9))
        self.anim_ax = self.anim.add_subplot(111, projection='3d')
        self.anim_ax.set_xlabel("$ L $")
        self.anim_ax.set_ylabel("$ L $")
        self.anim_ax.set_zlabel("$ L $")
        self.anim_ax.set_title("Spins")

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
                                              expand=False)
        self.canvas_anim.draw()
        self.toolbar_anim = NavigationToolbar2Tk(self.canvas_anim,
                                                 self.animation_frame)
        self.toolbar_anim.update()
        self.toolbar_anim.pack(side='top',
                               padx=0,
                               pady=0,
                               fill='both',
                               expand=False)

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
                                 interval=250, cache_frame_data=False)
        self.ani.pause()
        
        self.after(500,
                   lambda: Thread(target=self._export).start())
        
        # graph frame
        self.temp_frame = ctk.CTkFrame(self,
                                       height=1200)
        self.temp_frame.pack(side="top",
                              padx=5,
                              pady=5,
                              expand=True,
                              fill='both')

        self.temp_graph = Figure(figsize=(7, 7))
        self.temp_ax = self.temp_graph.add_subplot(111)
        self.temp_ax.set_xlabel("$ i $")
        self.temp_ax.set_ylabel("$ T $")
        self.temp_ax.plot(np.arange(self.iterations),
                          self.temp_cycle,
                          color="blue")
        self.temp_ax.axvline(x=0, color='k')
        self.temp_ax.axhline(y=0, color='k')
        self.temp_ax.set_title("Temperature cycle")
        self.temp_canvas = FigureCanvasTkAgg(self.temp_graph,
                                             self.temp_frame)
        self.temp_canvas.get_tk_widget().pack(side='top',
                                              padx=0,
                                              pady=0,
                                              fill='both',
                                              expand=False)
        self.toolbar_temp = NavigationToolbar2Tk(self.temp_canvas,
                                                 self.temp_frame)
        self.toolbar_temp.update()
        self.toolbar_temp.pack(side='top',
                               padx=0,
                               pady=0,
                               fill='both',
                               expand=False)

        self.energy_frame = ctk.CTkFrame(self,
                                         height=1200)
        self.energy_frame.pack(side="top",
                              padx=5,
                              pady=5,
                              expand=True,
                              fill='both')
        dx = self.temp_cycle[25::100]/4.511 - self.temp_cycle[:-25:100]/4.511
        dy = self.energy[25::100] - self.energy[:-25:100]
        self.energy_graph = Figure(figsize=(7, 7))
        self.energy_ax = self.energy_graph.add_subplot(111)
        self.energy_ax.set_xlabel(r"$ T\,/\,T_\mathrm{c} $")
        self.energy_ax.set_ylabel(r"$ E\,/\,\mathbf{\mathrm{k_B}} \, N \, T_\mathrm{c} $")
        self.energy_ax.plot(self.temp_cycle/4.511,
                            self.energy,
                            color="blue")
        self.energy_ax.quiver(self.temp_cycle[:-25:100]/4.511, 
                              self.energy[:-25:100], 
                              dx, dy, 
                              color='red', 
                              angles='xy',
                              scale_units='xy',
                              scale=5,
                              width=0.005)
        self.energy_ax.axhline(y=0, color='k')
        self.energy_ax.axvline(x=0, color='k')
        self.energy_ax.axvline(x=1, color='k', linestyle="--")
        self.energy_ax.set_title("Net Energy $E$")
        self.energy_ax.annotate("Start", xy=(self.temp_cycle[0]/4.511, self.energy[0]), xytext=(5, 5), textcoords='offset points')
        self.energy_ax.annotate("End", xy=(self.temp_cycle[-1]/4.511, self.energy[-1]), xytext=(5, -10), textcoords='offset points')
        self.energy_canvas = FigureCanvasTkAgg(self.energy_graph,
                                               self.energy_frame)
        self.energy_canvas.get_tk_widget().pack(side='top',
                                                padx=0,
                                                pady=0,
                                                fill='both',
                                                expand=False)
        self.toolbar_energy = NavigationToolbar2Tk(self.energy_canvas,
                                                   self.energy_frame)
        self.toolbar_energy.update()
        self.toolbar_energy.pack(side='top',
                                 padx=0,
                                 pady=0,
                                 fill='both',
                                 expand=False)
        
        self.mag_frame = ctk.CTkFrame(self,
                                      height=1200)
        self.mag_frame.pack(side="top",
                              padx=5,
                              pady=5,
                              expand=True,
                              fill='both')
        dx = self.temp_cycle[50::100]/4.511 - self.temp_cycle[:-50:100]/4.511
        dy = self.magnetization[50::100] - self.magnetization[:-50:100]
        self.magnetization_graph = Figure(figsize=(7, 7))
        self.magnetization_ax = self.magnetization_graph.add_subplot(111)
        self.magnetization_ax.set_xlabel(r"$ T\,/\,T_\mathrm{c} $")
        self.magnetization_ax.set_ylabel(r"$ M\,/\,\mu \, N $")
        self.magnetization_ax.plot(self.temp_cycle/4.511,
                                   self.magnetization,
                                   color="blue")
        self.magnetization_ax.quiver(self.temp_cycle[:-50:100]/4.511, 
                                     self.magnetization[:-50:100], 
                                     dx, dy, 
                                     color='red', 
                                     angles='xy',
                                     scale_units='xy',
                                     scale=5,
                                     width=0.005)
        self.magnetization_ax.axvline(x=0, color='k')
        self.magnetization_ax.axvline(x=1, color='k', linestyle="--")
        self.magnetization_ax.axhline(y=0, color='k')
        self.magnetization_ax.set_title("Net Magnetization $M$")
        self.magnetization_ax.annotate("Start", xy=(self.temp_cycle[0]/4.511, self.magnetization[0]), xytext=(5, 5), textcoords='offset points')
        self.magnetization_ax.annotate("End", xy=(self.temp_cycle[-1]/4.511, self.magnetization[-1]), xytext=(5, -10), textcoords='offset points')
        self.magnetization_canvas = FigureCanvasTkAgg(self.magnetization_graph,
                                                      self.mag_frame)
        self.magnetization_canvas.get_tk_widget().pack(side='top',
                                                       padx=0,
                                                       pady=0,
                                                       fill='both',
                                                       expand=False)
        self.toolbar_magnetization = NavigationToolbar2Tk(self.magnetization_canvas,
                                                          self.mag_frame)
        self.toolbar_magnetization.update()
        self.toolbar_magnetization.pack(side='top',
                                        padx=0,
                                        pady=0,
                                        fill='both',
                                        expand=False)
        
        if not Path(self.dir_path/"energy.png").is_file():
            self.energy_graph.savefig(self.dir_path/"energy.png")
            self.magnetization_graph.savefig(self.dir_path/"magnetization.png")
            self.temp_graph.savefig(self.dir_path/"temp_cycle.png")

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
                            pivot="middle",
                            colors=colors, length=0.6, normalize=True)
        self.anim_ax.set_title(f"Spins - Step {frame_idx}")
        self.anim_ax.set_xlim(0, self.L)
        self.anim_ax.set_ylim(0, self.L)
        self.anim_ax.set_zlim(0, self.L)
        self.anim_ax.grid(False)
        self.anim_ax.set_axis_off()
        self.canvas_anim.draw_idle()

    def _load_data(self):
        with open(self.dir_path/"config.bin", "rb") as f:
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
        self.iterations = self.grid_configuration["run_time"]

        self.temp_cycle = np.fromfile(self.dir_path/"temp_cycle.bin",
                                      dtype=np.float32)

        raw_atoms = np.fromfile(self.dir_path/"atoms.bin",
                                dtype=np.int8)
        self.atoms = raw_atoms.reshape((-1,
                                        self.grid_configuration["L"],
                                        self.grid_configuration["L"],
                                        self.grid_configuration["L"]))

        self.magnetization = np.fromfile(self.dir_path/"measurment.bin",
                                         dtype=np.int64,
                                         count=self.iterations)
        self.energy = np.fromfile(self.dir_path/"measurment.bin",
                                  dtype=np.float32,
                                  count=self.iterations,
                                  offset=self.iterations*np.dtype(np.int64).itemsize)

    def _export(self):
        if not Path(self.dir_path/"ising_simulation.mp4").is_file():
            print("Exporting...")
            fig_export = plt.figure(figsize=(8, 8))
            ax_export = fig_export.add_subplot(111, projection='3d')
            
            def update_export(frame_idx):
                print(f"{frame_idx+1}/{len(self.atoms)}")
                ax_export.clear()
                W = self.atoms[frame_idx].flatten()
                colors = np.where(W > 0, 'red', 'blue')
                ax_export.quiver(self.X, self.Y, self.Z,
                                    self.U, self.V, W,
                                    pivot="middle",
                                    colors=colors, length=0.6, normalize=True)
                ax_export.set_title(f"Spins - Step {frame_idx}")
                ax_export.set_xlim(0, self.L)
                ax_export.set_ylim(0, self.L)
                ax_export.set_zlim(0, self.L)
                ax_export.grid(False)
                ax_export.set_axis_off()

            ani_export = FuncAnimation(fig_export, update_export, frames=len(self.atoms))
            ani_export.save(
                self.dir_path / "ising_simulation.mp4", 
                writer="ffmpeg", 
                fps=7, 
                dpi=200, 
                bitrate=5000
            )
            plt.close(fig_export)
            print(f"Export finished {self.dir_path}/ising_simulation.mp4")
