import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from pathlib import Path
from BUS.KhachHangBUS import KhachHangBUS
from BUS.GiaoDichBUS import GiaoDichBUS
from DTO.GiaoDichDTO import GiaoDichDTO
from datetime import datetime

class TransactionRequestApp:
    def __init__(self, parent):
        # Đường dẫn gốc của dự án
        self.currentDir = Path(__file__).parent
        self.base_dir = self.currentDir.parent / "database"

        # Đường dẫn đến các thư mục
        self.reference_dir = os.path.join(self.base_dir, "Signatures", "Reference")
        self.current_dir = os.path.join(self.base_dir, "Signatures", "Current")
        self.model_dir = os.path.join(self.base_dir, "Models")
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "signature_model.keras")

        # Định dạng file hình ảnh được hỗ trợ
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

        # Khởi tạo BUS
        self.khach_hang_bus = KhachHangBUS()
        self.giao_dich_bus = GiaoDichBUS()

        # Tải mô hình và danh sách nhãn
        self.model, self.label_to_index, self.index_to_label = self.load_model_and_labels()

        # Tạo main frame trong parent (frame_right)
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Bảng điều khiển bên trái
        self.left_panel = ctk.CTkFrame(self.main_frame, width=320, height=650, fg_color="white")
        self.left_panel.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        # Bảng điều khiển bên phải
        self.right_panel = ctk.CTkFrame(self.main_frame, width=300, height=650, fg_color="white")
        self.right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)

        # Biến để lưu khách hàng được chọn và trạng thái xác thực
        self.selected_customer = None
        self.is_verified = ctk.BooleanVar(value=False)
        self.selected_image = None
        self.customer_window = None  # Biến để theo dõi cửa sổ "Chọn khách hàng"

        # Khởi tạo giao diện
        self.setup_ui()

    def load_model_and_labels(self):
        active_customers = [str(kh.MKH) for kh in self.khach_hang_bus.get_khach_hang_all() if kh.TT == 1]
        label_to_index = {str(mkh): idx for idx, mkh in enumerate(active_customers)}
        index_to_label = {idx: mkh for mkh, idx in label_to_index.items()}
        
        if os.path.exists(self.model_path):
            model = load_model(self.model_path)
            print(f"Đã tải mô hình từ {self.model_path}")
            return model, label_to_index, index_to_label
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy mô hình. Vui lòng huấn luyện mô hình trước.")
            return None, label_to_index, index_to_label

    def setup_ui(self):
        # Biến để theo dõi trạng thái giao dịch
        self.amount_entry = None
        self.transaction_btn = None
        self.print_btn = None
        self.verify_btn = None
        self.select_signature_btn = None
        self.signature_display = None
        self.signature_placeholder = None  # Nhãn cho placeholder
        self.result_label = None
        self.transaction_id_label = None  # Nhãn cho mã giao dịch

        # Font chữ cơ bản
        self.base_font = ("Arial", 14)
        self.bold_font = ("Arial", 14, "bold")

        # --- Bảng điều khiển bên trái ---
        # Chọn khách hàng
        customer_frame = ctk.CTkFrame(self.left_panel, fg_color="white")
        customer_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(customer_frame, text="CHỌN KHÁCH HÀNG:", font=self.bold_font, text_color="black").pack(anchor="w", pady=(0, 5))

        self.customer_name = ctk.CTkEntry(customer_frame, width=220, fg_color="white", text_color="black", font=self.base_font)
        self.customer_name.insert(0, "Tên khách hàng")
        self.customer_name.configure(state="readonly")
        self.customer_name.pack(side="left", padx=(0, 5))

        # Nhãn để cập nhật thông tin khách hàng
        self.info_labels = {}

        def reset_transaction_state():
            # Reset các trường giao diện
            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, "0")
            self.is_verified.set(False)
            self.result_label.configure(text="Kết quả xác thực: Chưa xác thực", text_color="red")
            self.transaction_btn.configure(state="disabled")
            self.print_btn.configure(state="disabled")

            # Cập nhật mã giao dịch mới
            max_mgd = self.giao_dich_bus.get_max_mgd()
            new_mgd = max_mgd + 1 if max_mgd else 1
            self.transaction_id_label.configure(text=f"Mã giao dịch: MGD{new_mgd:03d}")

            # Kiểm tra trạng thái khách hàng và vô hiệu hóa giao diện trước
            if self.selected_customer and self.selected_customer.TT != 1:
                messagebox.showwarning("Cảnh báo", "Khách hàng không thể giao dịch do Không hoạt động!")
                self.amount_entry.configure(state="disabled")
                self.verify_btn.configure(state="disabled")
                self.select_signature_btn.configure(state="disabled")
            else:
                self.amount_entry.configure(state="normal")
                self.verify_btn.configure(state="normal")
                self.select_signature_btn.configure(state="normal")

            # Xóa tham chiếu ảnh và hiển thị placeholder
            self.selected_image = None
            self.signature_display.pack_forget()  # Ẩn nhãn chứa ảnh
            self.signature_placeholder.pack(expand=True)  # Hiển thị nhãn placeholder

            # Xóa file current_signature.jpg trong thư mục Current
            current_signature_path = os.path.join(self.current_dir, "current_signature.jpg")
            if os.path.exists(current_signature_path):
                try:
                    os.remove(current_signature_path)
                    print(f"Deleted {current_signature_path}")
                except Exception as e:
                    print(f"Error deleting current_signature.jpg: {e}")

        def update_customer_info(customer):
            self.selected_customer = customer
            self.customer_name.configure(state="normal")
            self.customer_name.delete(0, "end")
            self.customer_name.insert(0, customer.HOTEN)
            self.customer_name.configure(state="readonly")
            self.info_labels["cccd"].configure(text=customer.CCCD)
            self.info_labels["phone"].configure(text=customer.SDT)
            self.info_labels["balance"].configure(text=f"{customer.TIEN:,} VND")
            self.info_labels["status"].configure(text="Hoạt động" if customer.TT == 1 else "Không hoạt động")
            reset_transaction_state()

        def show_customer_list():
            # Chỉ cho phép mở một cửa sổ duy nhất
            if self.customer_window is not None and self.customer_window.winfo_exists():
                self.customer_window.lift()  # Đưa cửa sổ hiện tại lên trên
                return

            self.customer_window = ctk.CTkToplevel(self.main_frame)
            self.customer_window.title("Chọn khách hàng")
            self.customer_window.geometry("450x400")
            self.customer_window.grab_set()  # Khóa tương tác với cửa sổ chính

            # Khi cửa sổ bị đóng, đặt lại biến customer_window
            self.customer_window.protocol("WM_DELETE_WINDOW", lambda: on_customer_window_close())

            def on_customer_window_close():
                self.customer_window.grab_release()  # Giải phóng khóa
                self.customer_window.destroy()
                self.customer_window = None

            search_frame = ctk.CTkFrame(self.customer_window)
            search_frame.pack(fill="x", padx=5, pady=5)
            ctk.CTkLabel(search_frame, text="Tìm theo CCCD:", font=self.base_font).pack(side="left")
            search_entry = ctk.CTkEntry(search_frame, font=self.base_font)
            search_entry.pack(side="left", padx=5)

            # Sử dụng tkinter Treeview vì customtkinter chưa có widget tương tự
            import tkinter.ttk as ttk
            columns = ("CCCD", "Tên khách hàng")
            tree = ttk.Treeview(self.customer_window, columns=columns, show="headings")
            tree.heading("CCCD", text="Số CCCD")
            tree.heading("Tên khách hàng", text="Tên khách hàng")
            tree.pack(fill="both", expand=True, padx=5, pady=5)

            item_to_cccd = {}

            def populate_list(search_text=""):
                for item in tree.get_children():
                    tree.delete(item)
                item_to_cccd.clear()
                for customer in self.khach_hang_bus.get_khach_hang_all():
                    if search_text.lower() in customer.CCCD.lower():
                        item_id = tree.insert("", "end", values=(customer.CCCD, customer.HOTEN))
                        item_to_cccd[item_id] = customer.CCCD

            populate_list()

            def search_customers(event=None):
                populate_list(search_entry.get())

            search_entry.bind("<KeyRelease>", search_customers)

            def select_customer():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Lỗi", "Vui lòng chọn một khách hàng!")
                    return
                item_id = selected_item[0]
                cccd = item_to_cccd.get(item_id)
                customer = self.khach_hang_bus.find_khach_hang_by_cccd(cccd)
                if customer:
                    update_customer_info(customer)
                    on_customer_window_close()  # Đóng cửa sổ sau khi chọn
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy khách hàng với CCCD này!")

            select_btn = ctk.CTkButton(self.customer_window, text="Chọn", command=select_customer, font=self.base_font, width=150, height=40)
            select_btn.pack(pady=10)

        select_customer_btn = ctk.CTkButton(customer_frame, text="...", width=40, height=40, font=self.base_font, command=show_customer_list)
        select_customer_btn.pack(side="left")

        # Thông tin khách hàng
        ctk.CTkLabel(self.left_panel, text="THÔNG TIN KHÁCH HÀNG:", font=self.bold_font, text_color="black", fg_color="white").pack(anchor="w", padx=10, pady=(10, 5))

        info_frame = ctk.CTkFrame(self.left_panel, fg_color="white")
        info_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(info_frame, text="Số CCCD:", fg_color="white", text_color="black", font=self.base_font).grid(row=0, column=0, sticky="e", pady=2)
        self.info_labels["cccd"] = ctk.CTkLabel(info_frame, text="000000000000", fg_color="white", text_color="black", font=self.base_font)
        self.info_labels["cccd"].grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))

        ctk.CTkLabel(info_frame, text="Số điện thoại:", fg_color="white", text_color="black", font=self.base_font).grid(row=1, column=0, sticky="e", pady=2)
        self.info_labels["phone"] = ctk.CTkLabel(info_frame, text="0123456789", fg_color="white", text_color="black", font=self.base_font)
        self.info_labels["phone"].grid(row=1, column=1, sticky="w", pady=2, padx=(10, 0))

        ctk.CTkLabel(info_frame, text="Số dư:", fg_color="white", text_color="black", font=self.base_font).grid(row=2, column=0, sticky="e", pady=2)
        self.info_labels["balance"] = ctk.CTkLabel(info_frame, text="0 VND", text_color="red", fg_color="white", font=self.base_font)
        self.info_labels["balance"].grid(row=2, column=1, sticky="w", pady=2, padx=(10, 0))

        ctk.CTkLabel(info_frame, text="Trạng thái:", fg_color="white", text_color="black", font=self.base_font).grid(row=3, column=0, sticky="e", pady=2)
        self.info_labels["status"] = ctk.CTkLabel(info_frame, text="Hoạt động", fg_color="white", text_color="black", font=self.base_font)
        self.info_labels["status"].grid(row=3, column=1, sticky="w", pady=2, padx=(10, 0))

        # Combobox loại giao dịch
        self.transaction_type = ctk.CTkComboBox(self.left_panel, values=["Rút tiền", "Nạp tiền"], state="readonly", width=220, font=self.base_font)
        self.transaction_type.set("Rút tiền")
        self.transaction_type.pack(anchor="w", padx=10, pady=10)

        # Số tiền giao dịch
        amount_frame = ctk.CTkFrame(self.left_panel, fg_color="white")
        amount_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(amount_frame, text="Số tiền giao dịch:", fg_color="white", text_color="black", font=self.base_font).pack(side="left")
        self.amount_entry = ctk.CTkEntry(amount_frame, width=120, font=self.base_font)
        self.amount_entry.insert(0, "0")
        self.amount_entry.pack(side="left", padx=5)
        ctk.CTkLabel(amount_frame, text="VND", fg_color="white", text_color="black", font=self.base_font).pack(side="left")

        # Mã giao dịch
        self.transaction_id_label = ctk.CTkLabel(self.left_panel, text="Mã giao dịch: MGD001", fg_color="white", text_color="black", font=self.base_font)
        self.transaction_id_label.pack(anchor="w", padx=10, pady=(0, 10))

        # Nút ở dưới cùng
        button_frame = ctk.CTkFrame(self.left_panel, fg_color="white")
        button_frame.pack(fill="x", padx=10, pady=(10, 0))

        def process_transaction():
            if not self.selected_customer:
                messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng!")
                return
            try:
                amount = int(self.amount_entry.get().replace(",", ""))
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
                return

            # Tính số tiền giao dịch
            transaction_amount = amount if self.transaction_type.get() == "Nạp tiền" else -amount
            new_balance = self.selected_customer.TIEN + transaction_amount

            if self.transaction_type.get() == "Rút tiền" and amount > self.selected_customer.TIEN:
                messagebox.showerror("Lỗi", "Số dư không đủ để rút tiền!")
                return

            # Lấy MGD mới
            max_mgd = self.giao_dich_bus.get_max_mgd()
            new_mgd = max_mgd + 1 if max_mgd else 1

            # Tạo đối tượng giao dịch
            giao_dich = GiaoDichDTO(
                MGD=new_mgd,
                MKH=self.selected_customer.MKH,
                MNV=1,  # NV1
                NGAYGIAODICH=datetime.now(),
                TIEN=transaction_amount,
                TIENKH=new_balance,
                TT=2  # Giao dịch thành công
            )

            # Lưu giao dịch
            self.giao_dich_bus.add_giao_dich(giao_dich)

            # Cập nhật số dư khách hàng
            self.selected_customer.TIEN = new_balance
            self.khach_hang_bus.update_khach_hang(self.selected_customer)

            # Xóa file current_signature.jpg sau khi giao dịch thành công
            current_signature_path = os.path.join(self.current_dir, "current_signature.jpg")
            if os.path.exists(current_signature_path):
                try:
                    os.remove(current_signature_path)
                    print(f"Deleted {current_signature_path} after transaction")
                except Exception as e:
                    print(f"Error deleting current_signature.jpg after transaction: {e}")

            # Cập nhật thông tin giao diện
            update_customer_info(self.selected_customer)
            messagebox.showinfo("Thông báo", "Giao dịch thành công")

        self.transaction_btn = ctk.CTkButton(button_frame, text="Giao dịch", fg_color="pink", text_color="white", width=140, height=50, font=self.base_font, command=process_transaction, state="disabled")
        self.transaction_btn.pack(side="left", padx=(0, 10))

        def print_receipt():
            messagebox.showinfo("Thông báo", "In thành công")

        self.print_btn = ctk.CTkButton(button_frame, text="In phiếu", fg_color="pink", text_color="white", width=140, height=50, font=self.base_font, command=print_receipt, state="disabled")
        self.print_btn.pack(side="left")

        # --- Bảng điều khiển bên phải ---
        # Chọn chữ ký
        signature_frame = ctk.CTkFrame(self.right_panel, fg_color="white")
        signature_frame.pack(fill="x", pady=(40, 10))

        def select_signature():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
            if file_path:
                try:
                    dest_path = os.path.join(self.current_dir, "current_signature.jpg")
                    os.makedirs(self.current_dir, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    
                    image = Image.open(file_path)
                    max_width, max_height = 200, 100
                    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    self.selected_image = ctk.CTkImage(light_image=image, size=(max_width, max_height))
                    
                    # Ẩn placeholder và hiển thị ảnh
                    self.signature_placeholder.pack_forget()
                    self.signature_display.configure(image=self.selected_image)
                    self.signature_display.pack(expand=True)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể tải ảnh: {e}")

        self.select_signature_btn = ctk.CTkButton(signature_frame, text="Chọn ảnh chữ ký", width=200, height=50, font=self.base_font, command=select_signature)
        self.select_signature_btn.pack()

        # Khu vực hiển thị chữ ký
        signature_display_frame = ctk.CTkFrame(self.right_panel, width=200, height=100, fg_color="lightgray")
        signature_display_frame.pack(pady=10)
        
        # Tạo hai nhãn: một cho placeholder, một cho ảnh
        self.signature_placeholder = ctk.CTkLabel(signature_display_frame, text="[Signature Placeholder]", fg_color="lightgray", text_color="black", font=self.base_font)
        self.signature_placeholder.pack(expand=True)
        
        self.signature_display = ctk.CTkLabel(signature_display_frame, text="", fg_color="lightgray", text_color="black")
        # Ban đầu ẩn nhãn chứa ảnh
        self.signature_display.pack_forget()

        # Nút xác nhận
        def verify_signature():
            if not self.selected_customer:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
                return

            current_signature_path = os.path.join(self.current_dir, "current_signature.jpg")
            if not os.path.exists(current_signature_path):
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh chữ ký!")
                self.is_verified.set(False)
                self.result_label.configure(text="Kết quả xác thực: Chưa xác thực", text_color="red")
                self.transaction_btn.configure(state="disabled")
                self.print_btn.configure(state="disabled")
                return

            if not self.model:
                messagebox.showerror("Lỗi", "Không có mô hình để xác thực. Vui lòng huấn luyện mô hình trước.")
                return

            img = load_img(current_signature_path, target_size=(200, 200))
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            predictions = self.model.predict(img_array)
            predicted_label = np.argmax(predictions, axis=1)[0]
            predicted_mkh = self.index_to_label.get(predicted_label, "Không xác định")
            confidence = predictions[0][predicted_label]

            threshold = 0.9
            if predicted_mkh == str(self.selected_customer.MKH) and confidence >= threshold:
                messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {self.selected_customer.MKH}\nConfidence: {confidence:.4f}")
                self.is_verified.set(True)
                self.result_label.configure(text="Kết quả xác thực: Đã xác thực", text_color="green")
                self.transaction_btn.configure(state="normal")
                self.print_btn.configure(state="normal")
            else:
                messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {self.selected_customer.MKH}\nTrùng khớp với MKH: {predicted_mkh}\nConfidence: {confidence:.4f}")
                self.is_verified.set(False)
                self.result_label.configure(text="Kết quả xác thực: Chưa xác thực", text_color="red")
                self.transaction_btn.configure(state="disabled")
                self.print_btn.configure(state="disabled")

        self.verify_btn = ctk.CTkButton(self.right_panel, text="Xác nhận", width=200, height=50, font=self.base_font, command=verify_signature)
        self.verify_btn.pack(pady=10)

        # Kết quả xác thực
        self.result_label = ctk.CTkLabel(self.right_panel, text="Kết quả xác thực: Chưa xác thực", fg_color="white", text_color="red", font=self.base_font)
        self.result_label.pack(pady=(10, 0))