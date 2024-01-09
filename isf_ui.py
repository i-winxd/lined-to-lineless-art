import os
import tkinter as tk
from tkinter import filedialog
from typing import Callable

from image_stroke_filler import make_lineless


class FileProcessorApp:
    fn: Callable[[str, str], None]
    a1: str
    a2: str
    initial_dir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, master: tk.Tk, fn: Callable[[str, str], None], a1: str, a2: str) -> None:
        self.a1 = a1
        self.a2 = a2
        self.fn = fn
        self.master = master
        self.master.title("File Processor App")

        self.file1_label = tk.Label(master, text=f"File 1 ({self.a1}):")
        self.file1_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)

        self.file1_entry = tk.Entry(master, state='readonly', width=40)
        self.file1_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_file1_button = tk.Button(master, text="Browse", command=self.browse_file1)
        self.browse_file1_button.grid(row=0, column=2, padx=10, pady=10)

        self.file2_label = tk.Label(master, text=f"File 2 ({self.a2}):")
        self.file2_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

        self.file2_entry = tk.Entry(master, state='readonly', width=40)
        self.file2_entry.grid(row=1, column=1, padx=10, pady=10)

        self.browse_file2_button = tk.Button(master, text="Browse", command=self.browse_file2)
        self.browse_file2_button.grid(row=1, column=2, padx=10, pady=10)

        self.run_button = tk.Button(master, text="Run", command=self.run_function)
        self.run_button.grid(row=2, column=1, pady=20)

    def browse_file1(self) -> None:
        initial_dir = self.initial_dir
        file_path = filedialog.askopenfilename(title=f"Open {self.a1}", initialdir=initial_dir,
                                               filetypes=[("PNG files", "*.png")])
        self.file1_entry.config(state='normal')
        self.file1_entry.delete(0, tk.END)
        self.file1_entry.insert(0, file_path)
        self.file1_entry.config(state='readonly')

    def browse_file2(self) -> None:
        initial_dir = self.initial_dir
        file_path = filedialog.askopenfilename(title=f"Open {self.a2}", initialdir=initial_dir,
                                               filetypes=[("PNG files", "*.png")])
        self.file2_entry.config(state='normal')
        self.file2_entry.delete(0, tk.END)
        self.file2_entry.insert(0, file_path)
        self.file2_entry.config(state='readonly')

    def run_function(self) -> None:
        file1_path = self.file1_entry.get()
        file2_path = self.file2_entry.get()

        if file1_path and file2_path:
            print("Executing run function with files:", file1_path, file2_path)
            self.fn(file1_path, file2_path)
            print("Run function successfully executed with files:", file1_path, file2_path)
        else:
            print("Please select both files before running the function.")

if __name__ == '__main__':
    root = tk.Tk()
    app = FileProcessorApp(root, make_lineless, "STROKE", "COLOR")
    root.mainloop()