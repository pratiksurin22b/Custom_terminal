import os
import subprocess
import webbrowser
import sys
import json
import tkinter as tk
from tkinter import messagebox

from network_diagnostics import execute_network_command
from shortcuts_loader import load_shortcuts
from utilities import log_output
from weather_handler import get_weather
from spotify_handler import handle_spotify
from news_handler import handle_news_command

def execute_command(command, text_area, root_area,self):
    command = command.strip()
    if not command:
        return

    # Special commands
    special_commands = {
        'exit': lambda: None,  # Will be handled in main.py
        'help': display_shortcuts,
        'sysinfo': system_info,
        'history': lambda: None,
        'date': show_datetime# Will be handled in main.py
    }
    
    network_commands = ['traceroute', 'portscan']
    
    # System control commands
    system_commands = ['shutdown', 'restart', 'sleep']

    if command.lower() in special_commands:
        special_commands[command.lower()]()
        return

    
    if command.lower() in system_commands:
        system_control(command.lower())
        return

    # Split the command into type and arguments
    parts = command.split(' ', 1)
    if len(parts) < 2:
        log_output(text_area, "Error: Command requires two arguments (type and path).")
        return

    command_type = parts[0].lower()
    rest_of_command = parts[1].strip()
    arguments = rest_of_command.split(' ')
    
    if command_type.lower() in network_commands:
        execute_network_command(command, text_area)
        return
    

    shortcuts = load_shortcuts()

    command_handlers = {
        'open': open_program,
        'folder': open_folder,
        'website': open_website,
        'run': run_shell_command,
        'search': perform_search,
        'ping' : network_ping,
        'theme': change_theme,
        'addshortcut' : add_new_shortcut,
        'weather' : get_weather,
        'spotify': handle_spotify,
        'news': lambda args, _, text_area, __, self: handle_news_command(args, text_area)
    }

    if command_type in command_handlers:
        command_handlers[command_type](arguments, shortcuts, text_area,root_area,self)
    else:
        log_output(text_area, f"Error: Unknown command type '{command_type}'.")

def add_new_shortcut(arguments, shortcuts, text_area, root_area, self):
    if len(arguments) < 3:
        log_output(text_area, "Usage: addshortcut <type> <shortcut_alias> <shortcutpath/url>")
        return

    shortcut_type = arguments[0].lower()
    shortcut_alias = arguments[1].lower()
    shortcut_path = arguments[2]
    
    valid_types = ['website', 'folder', 'open']
    
    if shortcut_type not in valid_types:
        log_output(text_area, f"Invalid shortcut type. Must be one of: {', '.join(valid_types)}")
        return

    def save_shortcut():
        alias = alias_entry.get().strip()
        path = path_entry.get().strip()

        if not alias or not path:
            messagebox.showerror("Error", "Both alias and path must be filled.")
            log_output(text_area, f"Both path and alias are not present.")
            return

        # Modify path if shortcut type is 'folder'
        if shortcut_type == 'folder':
            path = path.replace("\\", "\\\\")
        
        # Determine the JSON file based on shortcut type
        if shortcut_type == 'website':
            json_file = 'web_shortcuts.json'
        elif shortcut_type == 'folder':
            json_file = 'folder_shortcuts.json'
        elif shortcut_type == 'open':
            json_file = 'shortcuts.json'
        else:
            messagebox.showerror("Error", "Invalid shortcut type.")
            log_output(text_area, f"Invalid shortcut type: {shortcut_type}.")
            return

        # Load existing shortcuts
        try:
            with open(json_file, 'r') as f:
                shortcuts = json.load(f)
        except FileNotFoundError:
            shortcuts = {}

        shortcuts[alias] = path

        # Save the updated shortcuts
        with open(json_file, 'w') as f:
            json.dump(shortcuts, f, indent=4)

        log_output(text_area, f"Shortcut '{alias}' added successfully for {shortcut_type}.")
        shortcut_window.destroy()
    
    shortcut_window = tk.Toplevel(root_area)
    shortcut_window.title(f"Add {shortcut_type.capitalize()} Shortcut")
    shortcut_window.geometry("400x200")

    # Alias Label and Entry
    alias_label = tk.Label(shortcut_window, text="Shortcut Alias:")
    alias_label.pack(pady=(10, 0))
    alias_entry = tk.Entry(shortcut_window, width=50)
    alias_entry.insert(0, shortcut_alias)  # Pre-fill with command argument
    alias_entry.pack(pady=5)

    # Path/URL Label and Entry
    path_label = tk.Label(shortcut_window, text=f"{'URL' if shortcut_type == 'website' else 'Path'}:")
    path_label.pack(pady=(10, 0))
    path_entry = tk.Entry(shortcut_window, width=50)
    path_entry.insert(0, shortcut_path)  # Pre-fill with command argument
    path_entry.pack(pady=5)

    # Save Button
    save_button = tk.Button(shortcut_window, text="Save Shortcut", command=save_shortcut)
    save_button.pack(pady=10)

    
    
def open_program(arguments, shortcuts, text_area, _,self):
    if arguments and isinstance(arguments[0], str):
        path = arguments[0].strip()
        log_output(text_area, f"Opening program: {path}")

        if path in shortcuts["programs"]:
            command_to_run = shortcuts["programs"][path]
            try:
                result = subprocess.run([command_to_run], shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                log_output(text_area, f"Output:\n{output}")
            except Exception as e:
                log_output(text_area, f"Error: {e}")
        else:
            log_output(text_area, f"Error: Program path '{path}' not found in shortcuts.")
    else:
        log_output(text_area, "Error: Invalid arguments for opening program.")

def open_folder(arguments, shortcuts, text_area, _,self):
    if arguments and isinstance(arguments[0], str):
        path = arguments[0].strip()
        log_output(text_area, f"Opening folder: {path}")

        if path in shortcuts["folders"]:
            folder_path = shortcuts["folders"][path]
            try:
                if os.name == 'nt':  # For Windows
                    os.startfile(folder_path)
                else:
                    log_output(text_area, "Error: Folder opening is supported only on Windows for now.")
            except Exception as e:
                log_output(text_area, f"Error: {e}")
        else:
            log_output(text_area, f"Error: Folder path '{path}' not found in shortcuts.")
    else:
        log_output(text_area, "Error: Invalid arguments for opening folder.")

def open_website(arguments, shortcuts, text_area,_, self):
    if arguments and isinstance(arguments[0], str):
        path = arguments[0].strip()
        log_output(text_area, f"Opening website: {path}")

        if path in shortcuts["websites"]:
            website_url = shortcuts["websites"][path]
            try:
                webbrowser.open(website_url)
                log_output(text_area, f"Website '{path}' opened successfully.")
            except Exception as e:
                log_output(text_area, f"Error opening website '{path}': {e}")
        else:
            log_output(text_area, f"Error: Website shortcut '{path}' not found.")
    else:
        log_output(text_area, "Error: Invalid arguments for opening website.")

def display_shortcuts():
    shortcuts = load_shortcuts()
    output = ""
    
    if shortcuts["programs"]:
        output += "Program Shortcuts:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts["programs"].items()]) + "\n\n"
    else:
        output += "No program shortcuts available.\n\n"
    
    if shortcuts["folders"]:
        output += "Folder Shortcuts:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts["folders"].items()]) + "\n\n"
    else:
        output += "No folder shortcuts available.\n\n"
    
    if shortcuts["websites"]:
        output += "Website Shortcuts:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts["websites"].items()])
    else:
        output += "No website shortcuts available."
    
    return output

def available_themes():
    shortcuts=load_shortcuts()
    output=""
    
    
    if shortcuts["themes"]:
        output += "Available themes:\n" + "\n".join([f"{key}: {value}" for key, value in shortcuts["themes"].items()]) + "\n\n"
    else:
        output += "No folder shortcuts available.\n\n"
    
    return output
    
def run_shell_command(command, _, text_area, __, self):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        log_output(text_area, result.stdout if result.stdout else result.stderr)
    except Exception as e:
        log_output(text_area, f"Error running command: {e}")

def perform_search(arguments, _, text_area, __, self):
    log_output(text_area, f"Searching with the following arguments: {arguments}")
    query = " ".join(arguments)
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    log_output(text_area, f"Search query sent to Google: {query}")

def system_info():
    info = {
        "OS": os.name,
        "Platform": sys.platform,
        "Python Version": sys.version,
    }
    return "\n".join([f"{key}: {value}" for key, value in info.items()])

def system_control(action):
    if action == "shutdown":
        os.system("shutdown /s /t 0" if os.name == "nt" else "sudo shutdown now")
        return "Shutting down..."
    elif action == "restart":
        os.system("shutdown /r /t 0" if os.name == "nt" else "sudo reboot")
        return "Restarting..."
    elif action == "sleep":
        if os.name == "nt":  # Windows
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:  # macOS/Linux
            os.system("systemctl suspend")
        return "Entering sleep mode..."
    else:
        return "Invalid system control action."

def network_ping(arguments,_,text_area, __, self):
    if not arguments:
        log_output(text_area, "Usage: ping <hostname>")
        return
    
    host = arguments[0]
    try:
        result = subprocess.run(['ping', '-n', '4', host],capture_output=True, text=True)
        log_output(text_area, result.stdout)
    except Exception as e:
        log_output(text_area, f"Ping error: {e}")

def show_datetime():
    from datetime import datetime
    
    current_time = datetime.now()
    formats = {
        'full': "%Y-%m-%d %H:%M:%S",
    }
    return current_time.strftime(formats["full"])

THEME_CONFIG_FILE = 'last_theme.json'

def save_last_theme(theme_name):
    """Save the last used theme to a configuration file."""
    try:
        with open(THEME_CONFIG_FILE, 'w') as f:
            json.dump({"last_theme": theme_name}, f)
    except Exception as e:
        print(f"Error saving theme configuration: {e}")

def load_last_theme(shortcuts):
    """Load the last used theme from the configuration file."""
    try:
        if os.path.exists(THEME_CONFIG_FILE):
            with open(THEME_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                last_theme = config.get("last_theme")
                
                # Verify the theme exists in shortcuts
                if last_theme and last_theme in shortcuts["themes"]:
                    return last_theme
    except Exception as e:
        print(f"Error loading theme configuration: {e}")
    
    return None  # Return None if no valid theme found

def change_theme(arguments, shortcuts, text_area, root, self):
    if arguments and isinstance(arguments[0], str):
        theme_name = arguments[0].strip()
        log_output(text_area, f"Changing theme to: {theme_name}")

        if theme_name in shortcuts["themes"]:
            theme_settings = shortcuts["themes"][theme_name]
            try:
                # Configure root window
                root.configure(bg=theme_settings["bg"])
                
                # Configure main text area
                text_area.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    insertbackground=theme_settings["fg"]
                )
                
                # Configure entry and frame
                self.entry.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    insertbackground=theme_settings["fg"]
                )
                self.entry_frame.configure(bg=theme_settings["bg"])
                
                # Configure suggestion frame and components
                self.suggestion_frame.configure(bg=theme_settings["bg"])
                self.suggestion_list.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    selectbackground=theme_settings["fg"],
                    selectforeground=theme_settings["bg"]
                )
                self.preview_label.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"]
                )
                
                # Configure input container
                self.input_container.configure(bg=theme_settings["bg"])
                
                # Configure run button
                self.run_button.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    activebackground=theme_settings["bg"],
                    activeforeground=theme_settings["fg"]
                )
                
                # Save the current theme
                save_last_theme(theme_name)
                
                log_output(text_area, f"Theme '{theme_name}' applied successfully.")
                
            except Exception as e:
                log_output(text_area, f"Error applying theme: {e}")
        else:
            log_output(text_area, f"Error: Theme '{theme_name}' not found in available themes.")
    else:
        log_output(text_area, "Error: Invalid arguments for changing theme.")


    