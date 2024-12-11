import tkinter as tk
from tkinter import scrolledtext
import threading
import keyboard
import win32gui
import win32con

from command_executor import execute_command, display_shortcuts, system_info, system_control,show_datetime
from utilities import log_output

class CustomTerminal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Custom Terminal")
        self.root.geometry("+0+0")
        
        self.command_history = []
        self.is_expanded = False

        self.create_widgets()
        self.setup_hotkeys()

    def create_widgets(self):
        # Input frame
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(pady=5, padx=5, fill=tk.X)

        self.entry = tk.Entry(self.entry_frame, width=50)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry.bind('<Return>', self.on_execute_command)

        self.run_button = tk.Button(self.entry_frame, text="Run", command=self.on_execute_command)
        self.run_button.pack(side=tk.RIGHT, padx=5)

        # Scrollable text area
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

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
            

        # Execute the command
        execute_command(command, self.text_area)
        
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