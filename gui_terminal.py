import tkinter as tk
from tkinter import scrolledtext
import subprocess
import json
import os
import keyboard
import threading
import sys
import webbrowser
import pygetwindow as gw

# Load shortcuts from JSON files
def load_shortcuts():
    shortcuts = {}
    try:
        with open(r'F:\\Main_PROJECTS\\Custom_terminal\\shortcuts.json') as f:
            shortcuts["programs"] = json.load(f)
            log_output(f"DEBUG: Successfully loaded program shortcuts: {shortcuts['programs']}")
    except FileNotFoundError:
        log_output("DEBUG: shortcuts.json not found.")
        shortcuts["programs"] = {}
    except json.JSONDecodeError as e:
        log_output(f"DEBUG: JSON decode error in shortcuts.json: {e}")
        shortcuts["programs"] = {}
        
    try:
        with open(r'F:\\Main_PROJECTS\\Custom_terminal\\web_shortcuts.json') as f:
            shortcuts["websites"] = json.load(f)
            log_output(f"DEBUG: Successfully loaded website shortcuts: {shortcuts['websites']}")
    except FileNotFoundError:
        log_output("DEBUG: web_shortcuts.json not found.")
        shortcuts["websites"] = {}
    except json.JSONDecodeError as e:
        log_output(f"DEBUG: JSON decode error in web_shortcuts.json: {e}")
        shortcuts["websites"] = {}

    try:
        with open(r'F:\\Main_PROJECTS\\Custom_terminal\\folder_shortcuts.json') as f:
            shortcuts["folders"] = json.load(f)
            log_output(f"DEBUG: Successfully loaded folder shortcuts: {shortcuts['folders']}")
    except FileNotFoundError:
        log_output("DEBUG: shortcuts_folder.json not found.")
        shortcuts["folders"] = {}
    except json.JSONDecodeError as e:
        log_output(f"DEBUG: JSON decode error in shortcuts_folder.json: {e}")
        shortcuts["folders"] = {}

    return shortcuts

# Execute a shortcut or command with two arguments (type and path)
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
    elif command.lower() == 'sysinfo':
        system_info()
        return
    elif command.lower() in ['shutdown', 'restart', 'sleep']:
        system_control(command)

    # Split the command into the type and the path
    parts = command.split(' ', 1)
    if len(parts) < 2:
        log_output("Error: Command requires two arguments (type and path).")
        return

    command_type = parts[0].lower()
    rest_of_command = parts[1].strip()
    arguments = rest_of_command.split(' ')

    shortcuts = load_shortcuts()

    if command_type == 'open':
        open_program(arguments, shortcuts)
    elif command_type == 'folder':
        open_folder(arguments, shortcuts)
    elif command_type == 'website':
        open_website(arguments, shortcuts)
    elif command_type == 'run':
        run_shell_command(arguments)
    elif command_type == 'search':
        perform_search(arguments)

    else:
        log_output(f"Error: Unknown command type '{command_type}'. Supported types are 'open' and 'folder'.")

# Open a program (handle paths)
def open_program(path, shortcuts):
    log_output(f"Opening program: {path}")
    # Check if the path exists in the programs shortcuts
    if path in shortcuts["programs"]:
        command_to_run = shortcuts["programs"][path]
        try:
            result = subprocess.run([command_to_run], shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
        except Exception as e:
            output = f"Error: {e}"
        log_output(f"Output:\n{output}")
    else:
        log_output(f"Error: Program path '{path}' not found in shortcuts.")

# Open a folder in File Explorer (Windows)
def open_folder(path, shortcuts):
    log_output(f"Opening folder: {path}")
    # Check if the path exists in the folders shortcuts
    if path in shortcuts["folders"]:
        folder_path = shortcuts["folders"][path]
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(folder_path)  # Open folder in Explorer
            else:
                log_output(f"Error: Folder opening is supported only on Windows for now.")
        except Exception as e:
            output = f"Error: {e}"
            log_output(f"Output:\n{output}")
    else:
        log_output(f"Error: Folder path '{path}' not found in shortcuts.")
        
def open_website(path, shortcuts):
    log_output(f"Opening website: {path}")
    if path in shortcuts["websites"]:
        website_url = shortcuts["websites"][path]
        try:
            webbrowser.open(website_url)  # Open the URL in the default browser
            log_output(f"Website '{path}' opened successfully.")
        except Exception as e:
            log_output(f"Error opening website '{path}': {e}")
    else:
        log_output(f"Error: Website shortcut '{path}' not found.")
        
        
# Display available shortcuts
def display_shortcuts():
    shortcuts = load_shortcuts()
    if shortcuts["programs"]:
        output = "Program Shortcuts:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts["programs"].items()])
    else:
        output = "No program shortcuts available."
    log_output(output)

    if shortcuts["folders"]:
        output = "Folder Shortcuts:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts["folders"].items()])
    else:
        output = "No folder shortcuts available."
    log_output(output)

# Log output in the text area
def log_output(output):
    text_area.config(state=tk.NORMAL)##
    text_area.insert(tk.END, output + "\n")
    text_area.see(tk.END)
    text_area.config(state=tk.DISABLED)

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        log_output(result.stdout if result.stdout else result.stderr)
    except Exception as e:
        log_output(f"Error running command: {e}")

def perform_search(arguments):
    log_output(f"Searching with the following arguments: {arguments}")
    # Process the search as needed
    # For example, if it's a Google search:
    query = " ".join(arguments)  # Join all arguments into a single query
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    log_output(f"Search query sent to Google: {query}")
#

def system_info():
    info = {
        "OS": os.name,
        "Platform": sys.platform,
        "Python Version": sys.version,
    }
    log_output("\n".join([f"{key}: {value}" for key, value in info.items()]))
    
def system_control(action):
    if action == "shutdown":
        os.system("shutdown /s /t 0" if os.name == "nt" else "sudo shutdown now")
        log_output("Shutting down...")
    elif action == "restart":
        os.system("shutdown /r /t 0" if os.name == "nt" else "sudo reboot")
        log_output("Restarting...")
    elif action == "sleep":
        if os.name == "nt":  # Windows
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:  # macOS/Linux
            os.system("systemctl suspend")
        log_output("Entering sleep mode...")
    else:
        log_output("Invalid system control action.")


# Toggle window size between compact and expanded
def toggle_window_size():
    global is_expanded
    if is_expanded:
        entry_frame.pack_forget()
        text_area.pack_forget()
        entry_frame.pack(pady=5, padx=5, fill=tk.X)
        root.geometry("200x40")
    else:
        entry_frame.pack(pady=5, padx=5, fill=tk.X)
        text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        root.geometry("400x300")
    
    is_expanded = not is_expanded

# Toggle window minimize/restore
def toggle_window():
    if root.state() == "normal":
        root.iconify()
        entry.delete(0, tk.END)#
    else:
        root.deiconify()

        
def toggle_terminal_and_focus():
    if root.state() == "normal":
        root.iconify()
        root.focus()
        entry.delete(0, tk.END)
        # Minimize terminal
    else:
        root.deiconify()  # Restore terminal
        # Bring terminal to the foreground
        window = gw.getWindowsWithTitle("Custom Terminal")
        if window:
            window[0].activate()
        # Focus the entry widget
        entry.focus()

# Global hotkey listener
def all_hotkey():
    keyboard.add_hotkey('shift+1', toggle_window_size)
    keyboard.add_hotkey('shift+2', toggle_window)
    keyboard.add_hotkey('shift+3', toggle_terminal_and_focus)
    keyboard.wait()

# GUI Setup
root = tk.Tk()
root.title("Custom Terminal")
root.geometry("+0+0")  # Set the window position to (0,0)

is_expanded = False  # Flag to track window size

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
