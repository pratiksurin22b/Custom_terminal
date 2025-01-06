import tkinter as tk
from tkinter import scrolledtext
import threading
import keyboard
import win32gui
import win32con
import json

from command_executor import execute_command, display_shortcuts, system_info, system_control,show_datetime,available_themes
from utilities import log_output
from command_executor import load_last_theme, load_shortcuts
from network_diagnostics import execute_network_command
from news_handler import handle_news_command 

class CustomTerminal:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Custom Terminal")
        self.root.geometry("+0+0")
        
        self.command_history = []
        self.is_expanded = False
        
        self.command_tree =self.load_command_tree()

        self.create_widgets()
        self.setup_hotkeys()
        self.setup_autocomplete()

        # Load and apply the last used theme
        shortcuts = load_shortcuts()
        last_theme = load_last_theme(shortcuts)
        
        if last_theme:
            try:
                theme_settings = shortcuts["themes"][last_theme]
                self.root.configure(bg=theme_settings["bg"])
                
                self.text_area.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    insertbackground=theme_settings["fg"]
                )
                
                self.entry.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    insertbackground=theme_settings["fg"]
                )
                
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
                
                self.entry_frame.configure(bg=theme_settings["bg"])
                
                self.run_button.configure(
                    bg=theme_settings["bg"],
                    fg=theme_settings["fg"],
                    activebackground=theme_settings["bg"],
                    activeforeground=theme_settings["fg"]
                )
                
                log_output(self.text_area, f"Loaded last used theme: {last_theme}")
            except Exception as e:
                log_output(self.text_area, f"Error applying last theme: {e}")
                
    def load_command_tree(self):
            """Loads the command tree from a JSON file."""
            
            file_path = 'F:\\Main_PROJECTS\\Custom_terminal\\command_tree.json'
            try:
                with open(file_path, 'r') as file:
                    return json.load(file)
            except FileNotFoundError:
                print(f"Error: {file_path} not found. Using an empty command tree.")
                return {}
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON format in {file_path}: {e}")
                return {}
        
    def create_widgets(self):
        # Input frame
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(pady=5, padx=5, fill=tk.X)

        # Create a frame to hold the entry and suggestions
        self.input_container = tk.Frame(self.entry_frame)
        self.input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.entry = tk.Entry(self.input_container, width=50)
        self.entry.pack(fill=tk.X, expand=True)
        self.entry.bind('<Return>', self.on_execute_command)
        self.entry.bind('<KeyRelease>', self.on_entry_change)
        self.entry.bind('<Down>', self.focus_suggestion_list)
        
        self.entry.bind('<Escape>', self.hide_suggestions)
        self.entry.bind('<space>', self.handle_space)
        # Create suggestion listbox with command preview
        self.suggestion_frame = tk.Frame(self.input_container)
        
        self.suggestion_list = tk.Listbox(
            self.suggestion_frame,
            height=5,
            selectmode=tk.SINGLE,
            activestyle='dotbox'
        )
        
        self.suggestion_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.suggestion_list.bind('<Return>', self.use_suggestion)
        self.suggestion_list.bind('<Tab>', self.use_suggestion)
        self.suggestion_list.bind('<Escape>', self.hide_suggestions)
        self.suggestion_list.bind('<Double-Button-1>', self.use_suggestion)
        self.suggestion_list.bind('<<ListboxSelect>>', self.show_command_preview)
        

        self.suggestion_list.bind('<Up>', self.navigate_suggestions)
        self.suggestion_list.bind('<Down>', self.navigate_suggestions)
        self.suggestion_list.bind('<Left>', lambda e: self.entry.focus_set())
        self.suggestion_list.bind('<Right>', lambda e: self.entry.focus_set())
        # Add a preview label for showing command descriptions
        self.preview_label = tk.Label(
            self.suggestion_frame,
            text="",
            justify=tk.LEFT,
            wraplength=200,
            anchor='w'
        )
        self.preview_label.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)

        self.run_button = tk.Button(self.entry_frame, text="Run", command=self.on_execute_command)
        self.run_button.pack(side=tk.RIGHT, padx=5)

        # Scrollable text area
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

    def setup_autocomplete(self):
        self.suggestion_visible = False
        self.current_command_parts = []

    def get_current_suggestions(self, text):
        parts = text.strip().split()
        current_dict = self.command_tree
        
        # Handle empty input
        if not text:
            return list(current_dict.keys())
            
        # Navigate through command tree based on input parts
        for part in parts[:-1]:
            if part in current_dict:
                current_dict = current_dict[part]
            else:
                return []

        # Get suggestions for current level
        current_input = parts[-1].lower() if parts else ''
        suggestions = [
            cmd for cmd in current_dict.keys()
            if cmd.startswith(current_input)
        ]
        
        return suggestions

    def on_entry_change(self, event=None):
        if event.keysym in ('Return', 'Escape'):
            return

        current_text = self.entry.get().lower()
        suggestions = self.get_current_suggestions(current_text)
        
        if suggestions:
            self.show_suggestions(suggestions)
        else:
            self.hide_suggestions()

    def handle_space(self, event=None):
        # Store the current command part when space is pressed
        current_text = self.entry.get().strip()
        if current_text:
            self.current_command_parts.append(current_text.split()[-1])
            
        # Don't prevent the space from being entered
        return None

    def show_suggestions(self, suggestions):
        self.suggestion_list.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestion_list.insert(tk.END, suggestion)
        
        if not self.suggestion_visible:
            self.suggestion_frame.pack(fill=tk.X, expand=True)
            self.suggestion_visible = True

    def hide_suggestions(self, event=None):
        if self.suggestion_visible:
            self.suggestion_frame.pack_forget()
            self.suggestion_visible = False
            self.entry.focus_set()
            self.preview_label.config(text="")

    def show_command_preview(self, event=None):
        if not self.suggestion_list.curselection():
            return
            
        selected = self.suggestion_list.get(self.suggestion_list.curselection())
        current_text = self.entry.get()
        parts = current_text.split()
        
        # Build the complete command path
        command_path = parts[:-1] + [selected] if parts else [selected]
        
        # Check if there are subcommands
        current_dict = self.command_tree
        for part in command_path:
            if part in current_dict:
                current_dict = current_dict[part]
        
        if current_dict:  # Has subcommands
            preview = f"Subcommands available: {', '.join(current_dict.keys())}"
        else:  # Terminal command
            preview = "Terminal command"
            
        self.preview_label.config(text=preview)

    def handle_tab(self, event=None):
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_set()
        return 
    
    #handle handling for suggestion
    """def handle_tab(self, event=None):
        if self.suggestion_visible and self.suggestion_list.size() > 0:
            # If only one suggestion, use it
            if self.suggestion_list.size() == 1:
                self.suggestion_list.selection_set(0)
                self.use_suggestion(None)
            # If multiple suggestions but none selected, select first
            elif not self.suggestion_list.curselection():
                self.suggestion_list.selection_set(0)
                self.show_command_preview()
            # If one already selected, use it
            else:
                self.use_suggestion(None)
        return 'break' """ # Prevent default tab behavior

    def navigate_suggestions(self, event):
        """Handle up/down navigation in suggestion list"""
        if not self.suggestion_visible:
            return
        
        current_selection = self.suggestion_list.curselection()
        size = self.suggestion_list.size()
        
        if size == 0:
            return
            
        if not current_selection:
            # No selection yet, select first or last depending on key
            new_index = 0 if event.keysym == 'Down' else size - 1
        else:
            current_index = current_selection[0]
            if event.keysym == 'Down':
                new_index = (current_index + 1) % size
            else:  # Up
                new_index = (current_index - 1) % size
        
        self.suggestion_list.selection_clear(0, tk.END)
        self.suggestion_list.selection_set(new_index)
        self.suggestion_list.see(new_index)  # Ensure the selected item is visible
        self.show_command_preview()
        return 'break'  # Prevent default behavior

    def focus_suggestion_list(self, event):
        """Modified to properly handle initial focus on suggestion list"""
        if self.suggestion_visible and self.suggestion_list.size() > 0:
            self.suggestion_list.focus_set()
            # Only set selection if nothing is selected
            if not self.suggestion_list.curselection():
                self.suggestion_list.selection_set(0)
            self.show_command_preview()
        return 'break'  # Prevent default behavior

    def use_suggestion(self, event):
        if self.suggestion_list.curselection():
            selected = self.suggestion_list.get(self.suggestion_list.curselection())
            current_text = self.entry.get()
            parts = current_text.split()
            
            if parts:
                # Replace the last part with the selected suggestion
                new_text = ' '.join(parts[:-1] + [selected])
                
                
                
            else:
                new_text = selected
            
            
            self.entry.delete(0, tk.END)
            self.entry.insert(0, new_text)
            
            # Set focus and place the cursor at the end of the new text    
            self.entry.focus_set()
              # Set the cursor to the end of the text
            
           
            
            # Add space if there are subcommands available
            current_dict = self.command_tree
            for part in new_text.split():
                if part in current_dict:
                    current_dict = current_dict[part]
                    
            if current_dict:  # Has subcommands
                self.entry.insert(tk.END, ' ')
            
            self.hide_suggestions()
            self.entry.focus_set()
            self.entry.icursor(tk.END) 
            
            return "break"
            
    def on_execute_command(self, event=None):
        command = self.entry.get().strip()
        
        # Add to command history
        self.command_history.append(command)

        # Handle special commands
        if command.lower() == 'exit':
            self.root.destroy()
            return
        elif command.lower() == 'help':
            log_output(self.text_area, display_shortcuts())
            return
        elif command.lower() == 'showthemes':
            log_output(self.text_area,available_themes())
            return
        elif command.lower() == 'full':
            self.toggle_window_size()
            return
        elif command.lower() == 'sysinfo':
            log_output(self.text_area, system_info())
            return
        elif command.lower() in ['shutdown', 'restart', 'sleep']:
            log_output(self.text_area, system_control(command.lower()))
            return
        elif command.lower() == 'history':
            log_output(self.text_area, "\nCommand History:\n" + "\n".join(self.command_history))
            return
        elif command.lower() == 'date':
            log_output(self.text_area, "The date-time right now is:\t"+ show_datetime())
            return
        elif command.lower() == 'network-info':
            execute_network_command(command,self.text_area)
            return
        
        elif command.lower().startswith('news'):
            # Split the command into parts for the news handler
            command_parts = command.split()
            # Pass everything after 'news' as arguments
            args = command_parts[1:] if len(command_parts) > 1 else []
            handle_news_command(args, self.text_area)
            return

        
            
            

        # Execute the command
        execute_command(command, self.text_area, self.root,self)
        
        # Clear the entry after command execution
        self.entry.delete(0, tk.END)

    def toggle_window_size(self):
        if self.is_expanded:
            self.entry_frame.pack_forget()
            self.text_area.pack_forget()
            self.entry_frame.pack(pady=5, padx=5, fill=tk.X)
            self.root.geometry("200x40")
        else:
            self.entry_frame.pack(pady=5, padx=5, fill=tk.X)
            self.text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
            self.root.geometry("400x300")
        
        self.is_expanded = not self.is_expanded

    def toggle_window(self):
        if self.root.state() == "normal":
            self.root.iconify()
            self.entry.delete(0, tk.END)
        else:
            self.root.deiconify()

    def toggle_terminal_and_focus(self):
        if self.root.state() == "normal":
            self.root.iconify()
            self.entry.delete(0, tk.END)
        else:
            self.root.deiconify()
            
            try:
                self.root.lift()
                self.root.focus_force()
                self.entry.focus_set()
                
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                
            except Exception as e:
                log_output(self.text_area, f"Error activating window: {e}")

    def setup_hotkeys(self):
        def start_hotkey_listener():
            try:
                keyboard.add_hotkey('alt+shift+f1', self.toggle_window_size)
                keyboard.add_hotkey('alt+shift+f2', self.toggle_window)
                keyboard.add_hotkey('alt+shift+f3', self.toggle_terminal_and_focus)
                keyboard.wait()
            except Exception as e:
                log_output(self.text_area, f"Error in global hotkey listener: {e}")

        threading.Thread(target=start_hotkey_listener, daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    terminal = CustomTerminal()
    terminal.run()