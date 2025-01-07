import tkinter as tk
from themes_handler import load_last_theme
from shortcuts_loader import load_shortcuts

def send_email_interface():
  root=tk.Tk()
  root.title("Send email")
  root.geometry("+0+0")
  
  shortcuts=load_shortcuts()
  last_theme = load_last_theme(shortcuts)
  
  if last_theme:
    return