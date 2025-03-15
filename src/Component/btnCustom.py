import tkinter as tk

def create_buttons(self, btnText, bgColor):
    tk.Button(self.root, text = btnText, bg=bgColor).pack(pady=2)