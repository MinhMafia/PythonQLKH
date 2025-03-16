import customtkinter as csTk


def create_entry(app, label_text):
    csTk.CTkLabel(app, text=label_text).pack(pady=5)  # Hiển thị label
    entry = csTk.CTkEntry(app, width=250)
    entry.pack(pady=5)  # Hiển thị entry
    return entry  # Trả về entry để có thể sử dụng
