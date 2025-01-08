import tkinter as tk
from tkinter import filedialog

def log_output(text_area, output):
    text_area.config(state='normal')
    text_area.insert('end', output + "\n")
    text_area.see('end')
    text_area.config(state='disabled')
    
def browse_file_tkinter(attachment_path,attachment_listbox):
    # Open file dialog and let the user choose a file
    file_path = filedialog.askopenfilename(title="Select a File")
    if file_path:
        # If a file is selected, display the file path in the Entry widget
        
        attachment_path.append(file_path)
        attachment_listbox.insert(tk.END, file_path)