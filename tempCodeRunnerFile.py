
        self.root = tk.Tk()
        self.root.title("Custom Terminal")
        self.root.geometry("+0+0")
        
        self.command_history = []
        self.is_expanded = False

        self.create_widgets()
        self.setup_hotkeys()

    def create_widgets(self):