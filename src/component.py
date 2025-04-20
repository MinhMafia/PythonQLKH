import customtkinter as ctk
import tkinter.ttk as ttk


def CanGiuaCuaSo(window, width, height):
    window.resizable(width=False, height=False)
    screen_height = window.winfo_screenheight()
    screen_width = window.winfo_screenwidth()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

class CustomerWindow(ctk.CTkToplevel):
    def __init__(self, master, title, disabled_fields=None, prefill_data=None):
        super().__init__(master)
        self.title(title)
        comp.CanGiuaCuaSo(self, 400, 500)
        self.grab_set()
        self.focus()

        ctk.CTkLabel(self, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        self.fields = {}
        labels = ["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ"]
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=10)

        for label_text in labels:
            ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14)).pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.pack(pady=5)
            self.fields[label_text] = entry

        if disabled_fields:
            for field in disabled_fields:
                self.fields[field].configure(state="disabled")

        if prefill_data:
            self.fields["Mã Căn cước công dân"].insert(0, prefill_data[0])
            self.fields["Họ và Tên"].insert(0, prefill_data[1])
            self.fields["SĐT"].insert(0, prefill_data[2])
            self.fields["Email"].insert(0, prefill_data[3])
            self.fields["Địa chỉ"].insert(0, "Địa chỉ mẫu")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=self.close_window).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=self.close_window).pack(side="right", padx=10)

    def close_window(self):
        self.grab_release()
        self.destroy()

def show_notify(result, message, timeout=3000):
    """
    Hiển thị thông báo với trạng thái và nội dung.

    Args:
        result (bool): True nếu thành công, False nếu lỗi.
        message (str): Nội dung thông báo.
        timeout (int): Thời gian tự động đóng cửa sổ (ms). Mặc định là 3000ms.
    """
    notify_window = ctk.CTkToplevel()
    notify_window.title("Thông báo")
    notify_window.resizable(False, False)
    CanGiuaCuaSo(notify_window, 300, 150)
    notify_window.grab_set()
    notify_window.attributes("-topmost", True)  # Đảm bảo luôn ở trên cùng


    # Chọn tiêu đề và màu sắc dựa trên trạng thái
    title = "Thành công" if result else "Lỗi"
    color = "green" if result else "red"

    # Hiển thị tiêu đề
    ctk.CTkLabel(notify_window, text=title, font=("Arial", 16, "bold"), text_color=color).pack(pady=10)

    # Hiển thị nội dung thông báo
    ctk.CTkLabel(notify_window, text=message, font=("Arial", 14), wraplength=280).pack(pady=10)

    # Nút đóng
    ctk.CTkButton(notify_window, text="Đóng", command=notify_window.destroy).pack(pady=10)

    # Tự động đóng cửa sổ sau timeout (nếu được chỉ định)
    if timeout:
        notify_window.after(timeout, notify_window.destroy)