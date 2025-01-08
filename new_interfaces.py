import tkinter as tk

from themes_handler import load_last_theme
from shortcuts_loader import load_shortcuts
from utilities import browse_file_tkinter
import gmail_handler

def send_email_interface():
    # Create the Tkinter window
    root = tk.Tk()
    root.title("Email Sender")
    root.geometry("600x700")
    root.config(bg="#f4f4f9")  # Light background color for the window

    # Title label
    title_label = tk.Label(root, text="Email Sender", font=("Helvetica", 16, "bold"), bg="#f4f4f9")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Email components
    recipient_label = tk.Label(root, text="Recipient Email:", anchor="w", font=("Helvetica", 12), bg="#f4f4f9")
    recipient_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
    recipient_entry = tk.Entry(root, width=40, font=("Helvetica", 12))
    recipient_entry.grid(row=1, column=1, padx=20, pady=10)

    subject_label = tk.Label(root, text="Subject:", anchor="w", font=("Helvetica", 12), bg="#f4f4f9")
    subject_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
    subject_entry = tk.Entry(root, width=40, font=("Helvetica", 12))
    subject_entry.grid(row=2, column=1, padx=20, pady=10)

    body_label = tk.Label(root, text="Email Body:", anchor="w", font=("Helvetica", 12), bg="#f4f4f9")
    body_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
    body_text = tk.Text(root, height=10, width=40, font=("Helvetica", 12))
    body_text.grid(row=3, column=1, padx=20, pady=10)

    attachment_label = tk.Label(root, text="Attachment:", anchor="w", font=("Helvetica", 12), bg="#f4f4f9")
    attachment_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")

    attachment_path =[]
    
    #Listbox to show attachments paths
    attachment_listbox = tk.Listbox(root, height=5, width=40, font=("Helvetica", 12))
    attachment_listbox.grid(row=4, column=1, padx=20, pady=10)
    # Button to choose file
    
    #lambda used to pass additional parameters, as the command parameter expects function without brackets
    attachment_button = tk.Button(root, text="Choose File", font=("Helvetica", 12), command=lambda: browse_file_tkinter(attachment_path,attachment_listbox), relief="raised", bg="#4CAF50", fg="white")
    attachment_button.grid(row=5, column=1, padx=20, pady=10)

    # Send Email button
    send_button = tk.Button(root, text="Send Email", font=("Helvetica", 12, "bold"), command=None, relief="raised", bg="#2196F3", fg="white")
    send_button.grid(row=6, column=0, columnspan=2, pady=30)

    # Run the Tkinter window
    root.mainloop()
    
    

send_email_interface()
print()