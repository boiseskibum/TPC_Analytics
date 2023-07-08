import tkinter as tk
from tkinter import ttk

class ToggleWidgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Toggle Widget App")

        self.selected_option = tk.StringVar(value="Option 1")  # Control variable to track the selected option

        self.option1_radiobutton = ttk.Radiobutton(self, text="Option 1", variable=self.selected_option, value="Option 1", command=self.toggle_widgets)
        self.option1_radiobutton.pack(padx=10, pady=5)

        self.option2_radiobutton = ttk.Radiobutton(self, text="Option 2", variable=self.selected_option, value="Option 2", command=self.toggle_widgets)
        self.option2_radiobutton.pack(padx=10, pady=5)

        self.label1 = ttk.Label(self, text="This is Label 1")
        self.label2 = ttk.Label(self, text="This is Label 2")

        self.toggle_widgets()  # Initially show the selected option's widgets

    def toggle_widgets(self):
        selected_option = self.selected_option.get()

        if selected_option == "Option 1":
            self.label1.pack()
            self.label2.pack_forget()
        elif selected_option == "Option 2":
            self.label1.pack_forget()
            self.label2.pack()


if __name__ == "__main__":
    app = ToggleWidgetApp()
    app.mainloop()
