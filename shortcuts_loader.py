import json
import os

def load_shortcuts():
    shortcuts = {
        "programs": {},
        "websites": {},
        "folders": {},
        "themes" :{}
    }
    
    # Paths to your JSON files
    shortcut_files = [
        (r'F:\\Main_PROJECTS\\Custom_terminal\\shortcuts.json', "programs"),
        (r'F:\\Main_PROJECTS\\Custom_terminal\web_shortcuts.json', "websites"),
        (r'F:\Main_PROJECTS\\Custom_terminal\\folder_shortcuts.json', "folders"),
        (r'F:\Main_PROJECTS\\Custom_terminal\\themes.json', "themes")
    ]
    
    for file_path, key in shortcut_files:
        try:
            with open(file_path, 'r') as f:
                shortcuts[key] = json.load(f)
                print(f"DEBUG: Successfully loaded {key} shortcuts")
        except FileNotFoundError:
            print(f"DEBUG: {file_path} not found.")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error in {file_path}: {e}")
    
    return shortcuts