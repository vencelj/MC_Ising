from var_config import ConfigGUI, Variables
from pathlib import Path
from grid import Grid, InitMethods
from datetime import datetime
from threading import Thread
import subprocess
import platform


def generate_protocol(master):
    master.after(200,
                 lambda: master.winfo_toplevel().window_mannager(ConfigGUI.LOADING_WINDOW,
                                                                 load=True))

    master.after(500,
                 lambda: Thread(target=_process,
                                args=(master,),
                                daemon=True).start())


def _process(master):
    data_path = Path(master.winfo_toplevel(
    ).master_getter(Variables.DATA_PATH).get())
    app_path = Path(master.winfo_toplevel(
    ).master_getter(Variables.APP_PATH).get())
    if data_path != app_path:
        try:
            master.winfo_toplevel().master_setter(Variables.DATA_PATH, str(app_path))
            master.winfo_toplevel().window_opener(ConfigGUI.RESULTS_WINDOW,
                                                  data_path)
        except Exception:
            error_message = "File was corrupted.\nTry to create new one."
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.ERROR_WINDOW,
                                                                         load=True,
                                                                         message=error_message))
            return
        finally:
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.LOADING_WINDOW,
                                                                         load=False))
    else:
        try:
            time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
            dir_name = app_path.joinpath(f"./simulation_{time_stamp}")
            Path.mkdir(dir_name)
            grid = Grid(master=master)
            grid.create_config_txt(dir_name)
            grid.export_atoms(dir_name)
            grid.export_temp_cycle(dir_name)
        except Exception:
            error_message = "Parameters data type\nare incorect."
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.ERROR_WINDOW,
                                                                         load=True,
                                                                         message=error_message))
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.LOADING_WINDOW,
                                                                         load=False))
            return
        try:
            if platform.system() == "Windows":
                bin_path = ConfigGUI.get_path(master, r"./bin/simulant.exe")
            elif platform.system() == "linux":
                bin_path = ConfigGUI.get_path(master, r"./bin/simulant")
            result = subprocess.run([bin_path, str(dir_name.resolve())],
                                    capture_output=True, text=True)
            if result.returncode == 1:
                raise Exception()
        except Exception:
            error_message = "Simulation failed.\nTry again."
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.ERROR_WINDOW,
                                                                         load=True,
                                                                         message=error_message))
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.LOADING_WINDOW,
                                                                         load=False))
            return
        try:
            master.winfo_toplevel().window_opener(ConfigGUI.RESULTS_WINDOW,
                                                  dir_name.resolve())
        except Exception:
            error_message = "Results failed to load."
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.ERROR_WINDOW,
                                                                         load=True,
                                                                         message=error_message))
            return
        finally:
            master.after(200,
                         lambda: master.winfo_toplevel().window_mannager(ConfigGUI.LOADING_WINDOW,
                                                                         load=False))
