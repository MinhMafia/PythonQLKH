import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from PIL import Image, ImageTk
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

# Đường dẫn gốc của dự án
currentDir = Path(__file__).parent
base_dir = currentDir.parent / "database"

# Đường dẫn đến các thư mục
reference_dir = os.path.join(base_dir, "Signatures", "Reference")
current_dir = os.path.join(base_dir, "Signatures", "Current")
model_dir = os.path.join(base_dir, "Models")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "signature_model.keras")

# Định dạng file hình ảnh được hỗ trợ
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Khởi tạo BUS
khach_hang_bus = KhachHangBUS()
giao_dich_bus = GiaoDichBUS()

# Tải mô hình và danh sách nhãn
def load_model_and_labels():
    active_customers = [str(kh.MKH) for kh in khach_hang_bus.get_khach_hang_all() if kh.TT == 1]
    label_to_index = {str(mkh): idx for idx, mkh in enumerate(active_customers)}
    index_to_label = {idx: mkh for mkh, idx in label_to_index.items()}
    
    if os.path.exists(model_path):
        model = load_model(model_path)
        print(f"Đã tải mô hình từ {model_path}")
        return model, label_to_index, index_to_label
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy mô hình. Vui lòng huấn luyện mô hình trước.")
        return None, label_to_index, index_to_label

# Tải mô hình khi khởi động
model, label_to_index, index_to_label = load_model_and_labels()

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Yêu cầu giao dịch")
root.geometry("600x400")
root.option_add("*Font", "Arial 11")

# Tạo frame chính để chia trái và phải
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Bảng điều khiển bên trái
left_panel = tk.Frame(main_frame, width=320, height=650, bg="white")
left_panel.pack(side="left", fill="both", padx=10, pady=10, expand=True)

# Bảng điều khiển bên phải
right_panel = tk.Frame(main_frame, width=300, height=650, bg="white")
right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)

# Biến để lưu khách hàng được chọn và trạng thái xác thực
selected_customer = None
is_verified = tk.BooleanVar(value=False)
selected_image = None

# Biến để theo dõi trạng thái giao dịch
amount_entry = None
transaction_btn = None
print_btn = None
verify_btn = None
select_signature_btn = None
signature_display = None
result_label = None

# --- Bảng điều khiển bên trái ---
# Chọn khách hàng
customer_frame = tk.Frame(left_panel, bg="white")
customer_frame.pack(fill="x", pady=(10, 5))

tk.Label(customer_frame, text="CHỌN KHÁCH HÀNG:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=(0, 5))

customer_name = tk.Entry(customer_frame, width=30, bg="white", fg="black")
customer_name.insert(0, "Tên khách hàng")
customer_name.config(state="readonly")
customer_name.pack(side="left", padx=(0, 5))

# Nhãn để cập nhật thông tin khách hàng
info_labels = {}

def reset_transaction_state():
    global selected_image
    amount_entry.delete(0, tk.END)
    amount_entry.insert(0, "0")
    is_verified.set(False)
    result_label.config(text="Kết quả xác thực: Chưa xác thực", fg="red")
    transaction_btn.config(state="disabled")
    print_btn.config(state="disabled")
    selected_image = None
    signature_display.config(image="", text="[Signature Placeholder]")
    if selected_customer and selected_customer.TT != 1:
        amount_entry.config(state="disabled")
        verify_btn.config(state="disabled")
        select_signature_btn.config(state="disabled")
        messagebox.showwarning("Cảnh báo", "Khách hàng không thể giao dịch do Không hoạt động!")
    else:
        amount_entry.config(state="normal")
        verify_btn.config(state="normal")
        select_signature_btn.config(state="normal")

def update_customer_info(customer):
    global selected_customer
    selected_customer = customer
    customer_name.config(state="normal")
    customer_name.delete(0, tk.END)
    customer_name.insert(0, customer.HOTEN)
    customer_name.config(state="readonly")
    info_labels["cccd"].config(text=customer.CCCD)
    info_labels["phone"].config(text=customer.SDT)
    info_labels["balance"].config(text=f"{customer.TIEN:,} VND")
    info_labels["status"].config(text="Hoạt động" if customer.TT == 1 else "Không hoạt động")
    reset_transaction_state()

def show_customer_list():
    customer_window = tk.Toplevel(root)
    customer_window.title("Chọn khách hàng")
    customer_window.geometry("400x300")

    search_frame = tk.Frame(customer_window)
    search_frame.pack(fill="x", padx=5, pady=5)
    tk.Label(search_frame, text="Tìm theo CCCD:").pack(side="left")
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", padx=5)

    columns = ("CCCD", "Tên khách hàng")
    tree = ttk.Treeview(customer_window, columns=columns, show="headings")
    tree.heading("CCCD", text="Số CCCD")
    tree.heading("Tên khách hàng", text="Tên khách hàng")
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    item_to_cccd = {}

    def populate_list(search_text=""):
        for item in tree.get_children():
            tree.delete(item)
        item_to_cccd.clear()
        for customer in khach_hang_bus.get_khach_hang_all():
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
        customer = khach_hang_bus.find_khach_hang_by_cccd(cccd)
        if customer:
            update_customer_info(customer)
            customer_window.destroy()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy khách hàng với CCCD này!")

    select_btn = tk.Button(customer_window, text="Chọn", command=select_customer)
    select_btn.pack(pady=5)

select_customer_btn = tk.Button(customer_frame, text="...", width=3, command=show_customer_list)
select_customer_btn.pack(side="left")

# Thông tin khách hàng
tk.Label(left_panel, text="THÔNG TIN KHÁCH HÀNG:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=(10, 5))

info_frame = tk.Frame(left_panel, bg="white")
info_frame.pack(fill="x")

tk.Label(info_frame, text="Số CCCD:", bg="white").grid(row=0, column=0, sticky="w", pady=2)
info_labels["cccd"] = tk.Label(info_frame, text="082345124119", bg="white")
info_labels["cccd"].grid(row=0, column=1, sticky="w", pady=2)

tk.Label(info_frame, text="Số điện thoại:", bg="white").grid(row=1, column=0, sticky="w", pady=2)
info_labels["phone"] = tk.Label(info_frame, text="0123456789", bg="white")
info_labels["phone"].grid(row=1, column=1, sticky="w", pady=2)

tk.Label(info_frame, text="Số dư:", bg="white").grid(row=2, column=0, sticky="w", pady=2)
info_labels["balance"] = tk.Label(info_frame, text="500,000,000 VND", fg="red", bg="white")
info_labels["balance"].grid(row=2, column=1, sticky="w", pady=2)

tk.Label(info_frame, text="Trạng thái:", bg="white").grid(row=3, column=0, sticky="w", pady=2)
info_labels["status"] = tk.Label(info_frame, text="Hoạt động", bg="white")
info_labels["status"].grid(row=3, column=1, sticky="w", pady=2)

# Combobox loại giao dịch
transaction_type = ttk.Combobox(left_panel, values=["Rút tiền", "Nạp tiền"], state="readonly", width=20)
transaction_type.set("Rút tiền")
transaction_type.pack(anchor="w", pady=10)

# Số tiền giao dịch
amount_frame = tk.Frame(left_panel, bg="white")
amount_frame.pack(fill="x", pady=(0, 10))

tk.Label(amount_frame, text="Số tiền giao dịch:", bg="white").pack(side="left")
amount_entry = tk.Entry(amount_frame, width=15)
amount_entry.insert(0, "0")
amount_entry.pack(side="left", padx=5)
tk.Label(amount_frame, text="VND", bg="white").pack(side="left")

# Mã giao dịch
tk.Label(left_panel, text="Mã giao dịch: MGD004", bg="white").pack(anchor="w", pady=(0, 10))

# Nút ở dưới cùng
button_frame = tk.Frame(left_panel, bg="white")
button_frame.pack(fill="x", pady=(10, 0))

def process_transaction():
    if not selected_customer:
        messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng!")
        return
    try:
        amount = int(amount_entry.get().replace(",", ""))
    except ValueError:
        messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
        return

    # Tính số tiền giao dịch
    transaction_amount = amount if transaction_type.get() == "Nạp tiền" else -amount
    new_balance = selected_customer.TIEN + transaction_amount

    if transaction_type.get() == "Rút tiền" and amount > selected_customer.TIEN:
        messagebox.showerror("Lỗi", "Số dư không đủ để rút tiền!")
        return

    # Lấy MGD mới
    max_mgd = giao_dich_bus.get_max_mgd()
    new_mgd = max_mgd + 1 if max_mgd else 1

    # Tạo đối tượng giao dịch
    giao_dich = GiaoDichDTO(
        MGD=new_mgd,
        MKH=selected_customer.MKH,
        MNV=1,  # NV1
        NGAYGIAODICH=datetime.now(),
        TIEN=transaction_amount,
        TIENKH=new_balance,
        TT=2  # Giao dịch thành công
    )

    # Lưu giao dịch
    giao_dich_bus.add_giao_dich(giao_dich)

    # Cập nhật số dư khách hàng
    selected_customer.TIEN = new_balance
    khach_hang_bus.update_khach_hang(selected_customer)

    # Cập nhật thông tin giao dịch trên giao diện
    update_customer_info(selected_customer)
    messagebox.showinfo("Thông báo", "Giao dịch thành công")

transaction_btn = tk.Button(button_frame, text="Giao dịch", bg="pink", fg="white", width=10, command=process_transaction, state="disabled")
transaction_btn.pack(side="left", padx=(0, 10))

def print_receipt():
    messagebox.showinfo("Thông báo", "In thành công")

print_btn = tk.Button(button_frame, text="In phiếu", bg="pink", fg="white", width=10, command=print_receipt, state="disabled")
print_btn.pack(side="left")

# --- Bảng điều khiển bên phải ---
# Chọn chữ ký
signature_frame = tk.Frame(right_panel, bg="white")
signature_frame.pack(fill="x", pady=(0, 10))

def select_signature():
    global selected_image
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        try:
            dest_path = os.path.join(current_dir, "current_signature.jpg")
            os.makedirs(current_dir, exist_ok=True)
            shutil.copy2(file_path, dest_path)
            
            image = Image.open(file_path)
            max_width, max_height = 200, 100
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            selected_image = ImageTk.PhotoImage(image)
            signature_display.config(image=selected_image, text="")
            signature_display.image = selected_image
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải ảnh: {e}")

select_signature_btn = tk.Button(signature_frame, text="Chọn ảnh chữ ký", width=15, command=select_signature)
select_signature_btn.pack()

# Khu vực hiển thị chữ ký
signature_display_frame = tk.Frame(right_panel, width=200, height=100, bg="lightgray")
signature_display_frame.pack(pady=10)
signature_display_frame.pack_propagate(False)
signature_display = tk.Label(signature_display_frame, text="[Signature Placeholder]", bg="lightgray")
signature_display.pack(expand=True)

# Nút xác nhận
def verify_signature():
    if not selected_customer:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
        return

    customer_id = str(selected_customer.MKH)
    current_signature_path = os.path.join(current_dir, "current_signature.jpg")
    if not os.path.exists(current_signature_path):
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh chữ ký!")
        return

    if not model:
        messagebox.showerror("Lỗi", "Không có mô hình để xác thực. Vui lòng huấn luyện mô hình trước.")
        return

    img = load_img(current_signature_path, target_size=(200, 200))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    predictions = model.predict(img_array)
    predicted_label = np.argmax(predictions, axis=1)[0]
    predicted_mkh = index_to_label.get(predicted_label, "Không xác định")
    confidence = predictions[0][predicted_label]

    threshold = 0.9
    if predicted_mkh == customer_id and confidence >= threshold:
        messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {customer_id}\nConfidence: {confidence:.4f}")
        is_verified.set(True)
        result_label.config(text="Kết quả xác thực: Đã xác thực", fg="green")
        transaction_btn.config(state="normal")
        print_btn.config(state="normal")
    else:
        messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {customer_id}\nTrùng khớp với MKH: {predicted_mkh}\nConfidence: {confidence:.4f}")
        is_verified.set(False)
        result_label.config(text="Kết quả xác thực: Chưa xác thực", fg="red")
        transaction_btn.config(state="disabled")
        print_btn.config(state="disabled")

verify_btn = tk.Button(right_panel, text="Xác nhận", width=10, command=verify_signature)
verify_btn.pack(pady=10)

# Kết quả xác thực
result_label = tk.Label(right_panel, text="Kết quả xác thực: Chưa xác thực", fg="red", bg="white")
result_label.pack(pady=(10, 0))

# Khởi động ứng dụng
root.mainloop()