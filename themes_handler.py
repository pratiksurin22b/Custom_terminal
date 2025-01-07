from utilities import log_output
import json
import os

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