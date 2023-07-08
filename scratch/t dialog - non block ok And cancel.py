import tkinter as tk
import tkinter.simpledialog as sd
from PIL import Image, ImageTk
import time

def update_clock():
    current_time = time.strftime('%H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock)

#this is custom made dialog box to have ok cancel in it AND be non-blocking
class OKCancelDialog(sd.Dialog):
    def __init__(self, parent, title, message):
        self.title = title
        self.message = message
        super().__init__(parent)

    def body(self, master):
        tk.Label(master, text="This is a custom OK/Cancel dialog").pack()
        print(f"srt: {self.title}")
        print(f"srt: {self.message}")

    def buttonbox(self):


        box = tk.Frame(self)

        # Create the Tkinter window
        image = Image.open('jt.png')
        image = image.resize((60, 60))  # Resize to 150x150 pixels
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(box, image=photo)
        #label.pack()

        dialog_text = "Default ok or Cancel"
        label = tk.Label(box, text=dialog_text)
        label.pack()

        ok_button = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def ok(self):
        self.result = True
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

# Create the Tkinter window
window = tk.Tk()

# Define a function for the button command
def show_dialog():
    dialog = OKCancelDialog(window, "srt ok/cancel", "srt_message")  #this is custom dialog class created above
    print(f"dioalog:{dialog}")
    print(f"dialog.result:{dialog.result}")

    if dialog.result:
        print(f"You clicked OK: {dialog.result}")
    else:
        print(f"You clicked Cancel: {dialog.result}")

def open_dialog2():

#    result = tk.messagebox.askokcancel("Zero Calibration", "Make sure there is no weight")
    result = sd.askstring("Continue or Cancel", "enter string?")

    if result is not None:
        print(f"dialog2 You clicked Continue: {result}")
    else:
        print(f"dialog2 You clicked Cancel: {result}")

def open_dialog3():

    result = sd.askinteger("Continue or Cancel", "enter integer?")

    if result is not None:
        print(f"dialog3 You clicked Continue: {result}")
    else:
        print(f"dialog3 You clicked Cancel.{result}")

# Create the clock label
clock_label = tk.Label(window, font=('Arial', 24))
clock_label.pack(pady=20)

# Create a button to trigger the dialog
button = tk.Button(window, text="Show Dialog", command=show_dialog)
button.pack()

#button 2
button = tk.Button(window, text="Open Dialog2 messagebox.askokcancel", command=open_dialog2)
button.pack()

#button 3
button = tk.Button(window, text="Open Dialog3 integer", command=open_dialog3)
button.pack()


# Update the clock initially
update_clock()

# Start the Tkinter event loop
window.mainloop()
