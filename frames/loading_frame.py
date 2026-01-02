import customtkinter as ctk


class LoadingFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self,
                     text="Loading... This may take several minutes").pack(side="top",
                                                                           padx=5,
                                                                           pady=5,
                                                                           expand=False,
                                                                           fill="x")

        self.progress_bar = ctk.CTkProgressBar(self,
                                               orientation="horizontal",
                                               mode="indeterminate")
        self.progress_bar.pack(side="top",
                               padx=5,
                               pady=5,
                               expand=False,
                               fill="x")
        self.progress_bar.start()
