import customtkinter as ctk
import tkinter.ttk as ttk


def CanGiuaCuaSo(window, width, height):
    window.resizable(width=False, height=False)
    screen_height = window.winfo_screenheight()
    screen_width = window.winfo_screenwidth()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
