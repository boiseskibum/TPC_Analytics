import tkinter as tk
from tkinter import ttk

class RadioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Radio App")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Tab 1")

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Tab 2")

        self.label = ttk.Label(self.tab1, text="Label")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.radio_var = tk.StringVar()
        self.radio_var.set("show")

        self.radio_show = ttk.Radiobutton(self.tab1, text="Show", variable=self.radio_var, value="show",
                                          command=self.toggle_label)
        self.radio_show.grid(row=1, column=0, padx=10, pady=5)

        self.radio_hide = ttk.Radiobutton(self.tab1, text="Hide", variable=self.radio_var, value="hide",
                                          command=self.toggle_label)
        self.radio_hide.grid(row=2, column=0, padx=10, pady=5)

    def toggle_label(self):
        if self.radio_var.get() == "hide":
            self.label.grid_remove()  # Remove label from the grid
        else:
            self.label.grid()  # Add label back to the grid


if __name__ == "__main__":
    app = RadioApp()
    app.mainloop()
