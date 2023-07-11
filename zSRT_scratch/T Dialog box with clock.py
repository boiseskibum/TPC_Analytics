import tkinter as tk
import tkinter.simpledialog as sd
import time
from PIL import Image, ImageTk

def update_clock():
    current_time = time.strftime('%H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock)

icon_path = 'jt.png'
def open_dialog():

#    result = tk.messagebox.askokcancel("Zero Calibration", "Make sure there is no weight", icon='jt.png')
#    result = tk.messagebox.askokcancel("Zero Calibration", "Make sure there is no weight")

#    result = tk.messagebox.showinfo("Zero Calibration", "second string")

    result = sd.askstring("Continue or Cancel", "Do you want to continue?")
    if result is not None:
        print("You clicked Continue.")
    else:
        print("You clicked Cancel.")

def open_dialog2():

    result = tk.messagebox.askokcancel("Zero Calibration", "Make sure there is no weight")

#    result = tk.messagebox.showinfo("Zero Calibration", "second string")

    result = sd.askstring("Continue or Cancel", "Do you want to continue?")
    if result is not None:
        print("dialog2 You clicked Continue.")
    else:
        print("dialog2 You clicked Cancel.")


# Create the Tkinter window
window = tk.Tk()
window.title("Clock and Dialog Example")

image = Image.open('jt.png')
image = image.resize((60, 60))  # Resize to 150x150 pixels
photo = ImageTk.PhotoImage(image)

# Create a Label widget to display the image
label = tk.Label(window, image=photo)
label.pack()

# Create the clock label
clock_label = tk.Label(window, font=('Arial', 24))
clock_label.pack(pady=20)

# Create the button
button = tk.Button(window, text="Test Dialog", command=open_dialog)
button.pack()

# Create 2nd button
button = tk.Button(window, text="Test Dialog", command=open_dialog2)
button.pack()

# Update the clock initially
update_clock()

# Start the Tkinter event loop
window.mainloop()
