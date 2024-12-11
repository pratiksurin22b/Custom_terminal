def log_output(text_area, output):
    text_area.config(state='normal')
    text_area.insert('end', output + "\n")
    text_area.see('end')
    text_area.config(state='disabled')