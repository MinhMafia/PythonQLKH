import tkinter as tk

def create_entry(root, label_text):
    tk.Label(root.root, text = label_text).pack()
    entry = tk.Entry(root.root, width = 40 )
    entry.pack()
    return entry
