import tkinter as tk
from tkinter import scrolledtext
import subprocess
import json
import os
import keyboard  # Import the keyboard library
import threading  # For running the hotkey listener in a separate thread

# Load shortcuts from JSON file
def load_shortcuts():
    try:
        with open(r'F:\\Main_PROJECTS\\Custom_terminal\\shortcuts.json') as f:  # Update the path accordingly
            shortcuts = json.load(f)
            log_output(f"DEBUG: Successfully loaded shortcuts: {shortcuts}")
            return shortcuts
    except FileNotFoundError:
        log_output("DEBUG: shortcuts.json not found.")
        return {}
    except json.JSONDecodeError as e:
        log_output(f"DEBUG: JSON decode error: {e}")
        return {}

# Execute a shortcut or command
def execute_command():
    command = entry.get().strip()
    if not command:
        return
    if command.lower() == 'exit':
        root.destroy()
        return
    if command.lower() == 'help':
        display_shortcuts()
        return
    if command.lower() == 'full':
        toggle_window_size()
    
    shortcuts = load_shortcuts()
    if command in shortcuts:
        command_to_run = shortcuts[command]
    else:
        command_to_run = command

    log_output(f"Executing: {command_to_run}")  # Log the command being executed

    try:
        if os.name == 'nt' and command_to_run.startswith('"'):
            # For Windows, handle commands with full paths
            result = subprocess.run(command_to_run, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command_to_run, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
    except Exception as e:
        output = f"Error: {e}"
    
    log_output(f"> {command}\n{output}")

# Display available shortcuts
def display_shortcuts():
    shortcuts = load_shortcuts()
    if shortcuts:
        output = "Available shortcuts:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts.items()])
    else:
        output = "No shortcuts available. Add some to shortcuts.json."
    
    log_output(f"DEBUG: Displaying shortcuts: {output}")  # Debug log
    log_output(output)

# Log output in the text area
def log_output(output):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, output + "\n")
    text_area.see(tk.END)
    text_area.config(state=tk.DISABLED)

# Toggle window size between compact and expanded
def toggle_window_size():
    global is_expanded
    if is_expanded:
        # Switch to compact mode (hide the text area)
        entry_frame.pack_forget()
        text_area.pack_forget()
        entry_frame.pack(pady=5, padx=5, fill=tk.X)
        root.geometry("200x40")  # Set compact size
    else:
        # Switch to expanded mode (show the text area)
        entry_frame.pack(pady=5, padx=5, fill=tk.X)
        text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        root.geometry("400x300")  # Set expanded size
    
    is_expanded = not is_expanded  # Toggle the flag

def toggle_window():
    if root.state() == "normal":
        root.iconify()  # Minimize the window
    else:
        root.deiconify() 
    
def toggle_entry_focus():
    if root.focus_get() == entry:  # Check if the entry field currently has focus
        root.focus()  # Remove focus from the entry field
    else:
        entry.focus() 
        
# Listen for Shift+1 key press globally
def all_hotkey():
    keyboard.add_hotkey('shift+1', toggle_window_size)
    keyboard.add_hotkey('shift+2', toggle_window)
    keyboard.add_hotkey('shift+3', toggle_entry_focus)
    
    keyboard.wait()  # This will keep the listener running

# GUI Setup
root = tk.Tk()
root.title("Custom Terminal")

# Set window position to top-left
root.geometry("+0+0")  # Set the window position to (0,0) for top-left corner

# Flag to track whether we are in expanded mode
is_expanded = False

# Input field
entry_frame = tk.Frame(root)
entry_frame.pack(pady=5, padx=5, fill=tk.X)

entry = tk.Entry(entry_frame, width=50)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
entry.bind('<Return>', lambda _: execute_command())

run_button = tk.Button(entry_frame, text="Run", command=execute_command)
run_button.pack(side=tk.RIGHT, padx=5)

# Scrollable text area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, height=20)

# Run the global hotkey listener in a separate thread
threading.Thread(target=all_hotkey, daemon=True).start()
# Start the application
root.mainloop()
