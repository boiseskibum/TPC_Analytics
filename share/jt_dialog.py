import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class JT_Dialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title="default title", msg="default ok or cancel ", type ="okcancel"):
        self.msg = msg
        self.type = type   #valid is yesno, okcancel
        super().__init__(parent, title)

    def body(self, frame):

        # get longest len of a given line if there is multiple lines
        split_strings = self.msg.split("\n")
        longest_length = max(len(split) for split in split_strings)

        self.box_width = int(longest_length * .8)

        if self.box_width < 35:
            self.box_width = 35
        self.msg_label = tk.Label(frame, width=self.box_width, text=self.msg)
        self.msg_label.pack()
        return frame

    def ok_pressed(self):
        self.result = True
        self.destroy()

    def cancel_pressed(self):
        self.result = False
        self.destroy()

    def buttonbox(self):

        if self.type == "yesno":
            ok_text = 'Yes'
            cancel_text = 'No'
        elif self.type == "retrycancel":
                ok_text = 'Retry'
                cancel_text = 'Cancel'
        else:
            ok_text = 'OK'
            cancel_text = 'Cancel'

        #make default key have customer color for MacOS
#        style = ttk.Style()
#        style.theme_use("aqua")
#        style.configure("Default.TButton", background="#007AFF", foreground="white")

        pad = 6
        self.ok_button = ttk.Button(self, text=ok_text, width=12, command=self.ok_pressed, style="Default.TButton", default="active")
        if self.type == "ok":
            self.ok_button.pack(padx=pad, pady=pad)
        else:
            self.ok_button.pack(side="left", padx=pad, pady=pad)
        self.bind("<Return>", lambda event: self.ok_pressed())


        if self.type != "ok":
            cancel_button = ttk.Button(self, text=cancel_text, width=12, command=self.cancel_pressed)
            cancel_button.pack(side="right", padx=pad, pady=pad)
            self.bind("<Escape>", lambda event: self.cancel_pressed())

if __name__ == "__main__":

    def call_dialog(app):
        dialog = JT_Dialog(parent=app, title="SRT title for okcancel", msg="srt message really long text to see if this works in a bad example", type="okcancel")
        return dialog.result

    def main():
        app.title('Dialog')

        string_button = tk.Button(app, text='Show ok/cancel', width=25, command=show_dialog)
        string_button.pack()

        string_button = tk.Button(app, text='Show y/n', width=25, command=show_dialog2)
        string_button.pack()

        string_button = tk.Button(app, text='Show ok', width=25, command=show_dialog3)
        string_button.pack()

        string_button = tk.Button(app, text='Show multiline ok', width=25, command=show_dialog4)
        string_button.pack()

        exit_button = tk.Button(app, text='Close', width=25, command=app.destroy)
        exit_button.pack()

        app.mainloop()

    def show_dialog():
        result = call_dialog(app)
        print(result)

    def show_dialog2():
        dialog = JT_Dialog(parent=app, title="SRT Title for y/n that", msg="srt message text", type="yesno")
        print(dialog.result)

    def show_dialog3():
        dialog = JT_Dialog(parent=app, title="SRT Title for OK only", msg="srt message text", type="ok")
        print(dialog.result)

    def show_dialog4():
        dialog = JT_Dialog(parent=app, title="SRT Title for multi-line OK only",
               msg="srt message text\n 2nd line \n 3rd line this is a freaking reall long and crazy wide line that is ", type="ok")
        print(dialog.result)

    app = tk.Tk()

    main()