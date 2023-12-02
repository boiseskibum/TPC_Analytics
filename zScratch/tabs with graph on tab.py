import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graph App")
        self.geometry("600x400")  # Set the initial screen size

        self.tabControl = tk.ttk.Notebook(self)
        self.tab1 = tk.ttk.Frame(self.tabControl)
        self.tab2 = tk.ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text="Tab 1")
        self.tabControl.add(self.tab2, text="Tab 2")
        self.tabControl.pack(expand=1, fill="both")

        self.create_tab1()
        self.create_tab2()

    def create_tab1(self):
        # Button to display first graph on Tab 2
        btn1 = tk.Button(self.tab1, text="Display Graph 1", command=self.display_graph1)
        btn1.pack(pady=10)

        # Button to display second graph on Tab 2
        btn2 = tk.Button(self.tab1, text="Display Graph 2", command=self.display_graph2)
        btn2.pack(pady=10)

    def create_tab2(self):
        self.fig = plt.figure(figsize=(5, 5))  # Set the size of the graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab2)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self.tab2)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def display_graph1(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 'r-')
        ax.set_title("Graph 1")
        self.canvas.draw()

    def display_graph2(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot([1, 2, 3, 4, 5], [1, 4, 9, 16, 25], 'b-')
        ax.set_title("Graph 2")
        self.canvas.draw()


if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
