import tkinter as tk

def create_ok_dialog():
    dialog = tk.Toplevel()
    dialog.title("OK Dialog")

    # Add a label with your message
    label = tk.Label(dialog, text="This is a non-blocking OK dialog.")
    label.pack(padx=20, pady=20)

    # Add an OK button to close the dialog
    button_ok = tk.Button(dialog, text="OK", command=dialog.destroy)
    button_ok.pack(pady=10)

    # Add an OK button to close the dialog
    button_ok = tk.Button(dialog, text="OK", command=dialog.destroy)
    button_ok.pack(pady=10)

    # Set the dialog window to be non-blocking
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

# Create the Tkinter window
root = tk.Tk()

# Create a button to trigger the dialog
button = tk.Button(root, text="Show Dialog", command=create_ok_dialog)
button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()