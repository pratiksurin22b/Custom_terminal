import tkinter as tk
from command_executor import load_last_theme
from shortcuts_loader import load_shortcuts

def send_email_interface():
  root=tk.Tk()
  root.title("Send email")
  root.geometry("+0+0")
  
  shortcuts=load_shortcuts()
  last_theme = load_last_theme(shortcuts)
  