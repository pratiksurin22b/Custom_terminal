import os
import subprocess
import webbrowser
import sys

from shortcuts_loader import load_shortcuts
from utilities import log_output

def execute_command(command, text_area):
    command = command.strip()
    if not command:
        return

    # Special commands
    special_commands = {
        'exit': lambda: None,  # Will be handled in main.py
        'help': display_shortcuts,
        'sysinfo': system_info,
        'history': lambda: None,  # Will be handled in main.py
    }

    if command.lower() in special_commands:
        special_commands[command.lower()]()
        return

    # System control commands
    system_commands = ['shutdown', 'restart', 'sleep']
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

    shortcuts = load_shortcuts()

    command_handlers = {
        'open': open_program,
        'folder': open_folder,
        'website': open_website,
        'run': run_shell_command,
        'search': perform_search,
        'ping' : network_ping
    }

    if command_type in command_handlers:
        command_handlers[command_type](arguments, shortcuts, text_area)
    else:
        log_output(text_area, f"Error: Unknown command type '{command_type}'.")

def open_program(arguments, shortcuts, text_area):
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

def open_folder(arguments, shortcuts, text_area):
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

def open_website(arguments, shortcuts, text_area):
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

def run_shell_command(command, _, text_area):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        log_output(text_area, result.stdout if result.stdout else result.stderr)
    except Exception as e:
        log_output(text_area, f"Error running command: {e}")

def perform_search(arguments, _, text_area):
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

def network_ping(arguments,_,text_area):
    if not arguments:
        log_output(text_area, "Usage: ping <hostname>")
        return
    
    host = arguments[0]
    try:
        result = subprocess.run(['ping', '-c', '4', host],capture_output=True, text=True)
        log_output(text_area, result.stdout)
    except Exception as e:
        log_output(text_area, f"Ping error: {e}")