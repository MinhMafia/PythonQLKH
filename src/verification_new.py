import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, Flatten, Input, Dropout
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from DTO.KhachHangDTO import KhachHangDTO
from BUS.KhachHangBUS import KhachHangBUS
from pathlib import Path 
from sklearn.model_selection import train_test_split

# Đường dẫn gốc của dự án
currentDir = Path(__file__).parent
base_dir = currentDir.parent / "database"

# Đường dẫn đến các thư mục
reference_dir = os.path.join(base_dir, "Signatures", "Reference")
current_dir = os.path.join(base_dir, "Signatures", "Current")
new_customer_dir = os.path.join(base_dir, "Signatures", "new_customer")
model_dir = os.path.join(base_dir, "Models")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "signature_model.keras")

# Định dạng file hình ảnh được hỗ trợ
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Hàm tính entropy của dự đoán
def calculate_entropy(predictions):
    epsilon = 1e-10  # Tránh log(0)
    entropy = -np.sum(predictions * np.log(predictions + epsilon))
    return entropy

# Hàm huấn luyện mô hình VGG16 với tăng cường dữ liệu
def train_vgg16_model():
    # Lấy danh sách khách hàng có trạng thái 0 (Bị khóa) hoặc 1 (Hoạt động) và có thư mục chữ ký mẫu
    all_customers = KhachHangBUS().get_khach_hang_all()
    eligible_customers = []
    for kh in all_customers:
        if kh.TT in [0, 1]:  # Bao gồm cả khách hàng bị khóa và hoạt động
            customer_dir = os.path.join(reference_dir, str(kh.MKH))
            if os.path.exists(customer_dir) and any(
                file.lower().endswith(image_extensions) for file in os.listdir(customer_dir)
            ):
                eligible_customers.append(str(kh.MKH))
    
    classes = eligible_customers  
    
    if not eligible_customers:
        print("Không có khách hàng nào đủ điều kiện để huấn luyện mô hình.")
        return None, None, None
    
    # Chuẩn bị dữ liệu huấn luyện
    X = []
    y = []
    label_to_index = {cls: idx for idx, cls in enumerate(classes)}
    index_to_label = {idx: cls for cls, idx in label_to_index.items()}
    
    # Tải dữ liệu từ khách hàng
    for mkh in eligible_customers:
        customer_dir = os.path.join(reference_dir, str(mkh))
        for file in os.listdir(customer_dir):
            if file.lower().endswith(image_extensions):
                image_path = os.path.join(customer_dir, file)
                img = load_img(image_path, target_size=(200, 200))
                img_array = img_to_array(img)
                img_array = preprocess_input(img_array)
                X.append(img_array)
                y.append(label_to_index[str(mkh)])
    
    if len(X) == 0:
        print("Không có dữ liệu chữ ký mẫu để huấn luyện mô hình.")
        return None, None, None

    X = np.array(X)
    y = np.array(y)
    y = tf.keras.utils.to_categorical(y, num_classes=len(classes))
    
    # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Tăng cường dữ liệu mạnh hơn
    datagen = ImageDataGenerator(
        rotation_range=30,           # Xoay ngẫu nhiên trong khoảng ±30 độ
        width_shift_range=0.15,     # Dịch chuyển ngang ±15%
        height_shift_range=0.15,    # Dịch chuyển dọc ±15%
        brightness_range=[0.7, 1.3],# Thay đổi độ sáng từ 70% đến 130%
        zoom_range=0.3,             # Thu phóng ±30%
        shear_range=0.2,            # Thêm biến dạng cắt
        horizontal_flip=False,      # Không lật ngang
        fill_mode='nearest'
    )
    
    # Tạo iterator cho tập huấn luyện
    batch_size = 16  # Giảm batch_size để phù hợp với dữ liệu nhỏ
    train_generator = datagen.flow(X_train, y_train, batch_size=batch_size)
    
    # Không tăng cường dữ liệu cho tập kiểm tra
    val_datagen = ImageDataGenerator()
    val_generator = val_datagen.flow(X_val, y_val, batch_size=batch_size)
    
    # Xây dựng mô hình VGG16
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(200, 200, 3))
    for layer in base_model.layers:
        layer.trainable = False
    
    x = base_model.output
    x = Flatten()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)  # Thêm Dropout để giảm overfitting
    predictions = Dense(len(classes), activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Biên dịch mô hình
    model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Đảm bảo steps_per_epoch và validation_steps không bằng 0
    steps_per_epoch = max(1, len(X_train) // batch_size)
    validation_steps = max(1, len(X_val) // batch_size)
    
    # Huấn luyện mô hình
    model.fit(
        train_generator,
        epochs=15,
        steps_per_epoch=steps_per_epoch,
        validation_data=val_generator,
        validation_steps=validation_steps,
        verbose=1
    )
    
    # Lưu mô hình
    model.save(model_path)
    print(f"Đã huấn luyện và lưu mô hình tại {model_path}")
    
    return model, label_to_index, index_to_label

# Tải mô hình và danh sách nhãn
def load_model_and_labels():
    all_customers = KhachHangBUS().get_khach_hang_all()
    eligible_customers = []
    for kh in all_customers:
        if kh.TT in [0, 1]:
            customer_dir = os.path.join(reference_dir, str(kh.MKH))
            if os.path.exists(customer_dir) and any(
                file.lower().endswith(image_extensions) for file in os.listdir(customer_dir)
            ):
                eligible_customers.append(str(kh.MKH))
    
    classes = eligible_customers  # Không có lớp "unknown"
    label_to_index = {cls: idx for idx, cls in enumerate(classes)}
    index_to_label = {idx: cls for cls, idx in label_to_index.items()}
    
    if os.path.exists(model_path):
        model = load_model(model_path)
        print(f"Đã tải mô hình từ {model_path}")
        return model, label_to_index, index_to_label
    else:
        print("Không tìm thấy mô hình. Huấn luyện mô hình mới...")
        model, label_to_index, index_to_label = train_vgg16_model()
        return model, label_to_index, index_to_label

# Tải mô hình khi khởi động
model, label_to_index, index_to_label = load_model_and_labels()

# Giao diện đồ họa
class SignatureVerificationApp:
    def __init__(self, parent_frame):
        self.root = parent_frame
        self.khach_hang_bus = KhachHangBUS()

        # Font chữ cơ bản
        self.base_font = ("Arial", 12)
        self.bold_font = ("Arial", 12, "bold")

        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        
        # Tab 1: Thêm chữ ký mẫu
        self.tab_add_customer = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_add_customer, text="Thêm chữ ký mẫu")
        
        # Tab 2: Xác thực chữ ký
        self.tab_verify = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_verify, text="Xác thực chữ ký")
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        self.setup_add_customer_tab()
        self.setup_verify_tab()
        
        # Danh sách ảnh tạm thời cho khách hàng mới và biến theo dõi cửa sổ
        self.selected_images = []
        self.selected_customer_id = None
        self.add_customer_window = None  # Biến theo dõi cửa sổ chọn khách hàng ở tab "Thêm chữ ký mẫu"
        self.verify_customer_window = None  # Biến theo dõi cửa sổ chọn khách hàng ở tab "Xác thực chữ ký"

    def setup_add_customer_tab(self):
        # Phần trên: Danh sách khách hàng chưa kích hoạt
        frame_list = ttk.LabelFrame(self.tab_add_customer, text="Danh sách khách hàng chưa kích hoạt", padding=10)
        frame_list.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("MKH", "CCCD", "Name")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", height=8)
        self.tree.heading("MKH", text="Mã khách hàng")
        self.tree.heading("CCCD", text="Số CCCD")
        self.tree.heading("Name", text="Họ và tên")
        self.tree.column("MKH", width=100, anchor="center")
        self.tree.column("CCCD", width=150, anchor="center")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(frame_list, text="Làm mới danh sách", command=self.refresh_customer_list).pack(pady=5)

        # Phần dưới: Thêm chữ ký mẫu
        frame_add = ttk.LabelFrame(self.tab_add_customer, text="Thêm chữ ký mẫu", padding=10)
        frame_add.pack(fill="both", expand=True, padx=5, pady=5)

        # Chọn khách hàng (Entry + Button)
        customer_frame = ttk.Frame(frame_add)
        customer_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(customer_frame, text="Tên khách hàng:", font=self.bold_font).pack(side="left", padx=(0, 5))
        self.customer_name_entry = ttk.Entry(customer_frame, font=self.base_font, width=30)
        self.customer_name_entry.insert(0, "Chọn khách hàng")
        self.customer_name_entry.configure(state="readonly")
        self.customer_name_entry.pack(side="left", padx=(0, 5))

        def show_customer_list():
            # Chỉ cho phép mở một cửa sổ duy nhất
            if self.add_customer_window is not None and self.add_customer_window.winfo_exists():
                self.add_customer_window.lift()
                return

            self.add_customer_window = tk.Toplevel(self.root)
            self.add_customer_window.title("Chọn khách hàng")
            self.add_customer_window.geometry("600x400")
            self.add_customer_window.grab_set()

            self.add_customer_window.protocol("WM_DELETE_WINDOW", lambda: on_customer_window_close())

            def on_customer_window_close():
                self.add_customer_window.grab_release()
                self.add_customer_window.destroy()
                self.add_customer_window = None

            # Tìm kiếm khách hàng
            search_frame = ttk.Frame(self.add_customer_window)
            search_frame.pack(fill="x", padx=5, pady=5)
            ttk.Label(search_frame, text="Tìm theo CCCD:", font=self.base_font).pack(side="left")
            search_entry = ttk.Entry(search_frame, font=self.base_font)
            search_entry.pack(side="left", padx=5, fill="x", expand=True)

            # Bảng khách hàng
            columns = ("MKH", "CCCD", "Name")
            tree = ttk.Treeview(self.add_customer_window, columns=columns, show="headings", height=10)
            tree.heading("MKH", text="Mã khách hàng")
            tree.heading("CCCD", text="Số CCCD")
            tree.heading("Name", text="Họ và tên")
            tree.column("MKH", width=100, anchor="center")
            tree.column("CCCD", width=150, anchor="center")
            tree.column("Name", width=200, anchor="w")
            tree.pack(fill="both", expand=True, padx=5, pady=5)

            item_to_mkh = {}

            def populate_list(search_text=""):
                for item in tree.get_children():
                    tree.delete(item)
                item_to_mkh.clear()
                for customer in self.khach_hang_bus.get_khach_hang_all():
                    if customer.TT == 2 and (search_text.lower() in customer.CCCD.lower()):
                        item_id = tree.insert("", "end", values=(customer.MKH, customer.CCCD, customer.HOTEN))
                        item_to_mkh[item_id] = customer.MKH

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
                mkh = item_to_mkh.get(item_id)
                customer = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(int(mkh))
                if customer:
                    self.selected_customer_id = str(customer.MKH)
                    self.customer_name_entry.configure(state="normal")
                    self.customer_name_entry.delete(0, "end")
                    self.customer_name_entry.insert(0, customer.HOTEN)
                    self.customer_name_entry.configure(state="readonly")
                    self.selected_images = []
                    self.image_listbox.delete(0, tk.END)
                    messagebox.showinfo("Thông báo", f"Đã chọn khách hàng {self.selected_customer_id}. Vui lòng thêm ít nhất 3 ảnh chữ ký mẫu.")
                    on_customer_window_close()

            ttk.Button(self.add_customer_window, text="Chọn", command=select_customer).pack(pady=10)

        ttk.Button(customer_frame, text="...", width=5, command=show_customer_list).pack(side="left")

        # Danh sách ảnh chữ ký
        ttk.Label(frame_add, text="Ảnh chữ ký đã chọn:", font=self.bold_font).pack(anchor="w", padx=5, pady=5)
        self.image_listbox = tk.Listbox(frame_add, height=5, font=self.base_font)
        self.image_listbox.pack(fill="x", padx=5, pady=5)

        # Nút thêm ảnh và lưu trữ
        button_frame = ttk.Frame(frame_add)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Thêm ảnh chữ ký", command=self.add_signature_images).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Lưu trữ", command=self.save_signatures).pack(side="right", padx=5)

        self.refresh_customer_list()

    def setup_verify_tab(self):
        frame_verify = ttk.LabelFrame(self.tab_verify, text="Xác thực chữ ký khách hàng", padding=10)
        frame_verify.pack(fill="both", expand=True, padx=5, pady=5)

        # Chọn khách hàng (Entry + Button)
        customer_frame = ttk.Frame(frame_verify)
        customer_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(customer_frame, text="Tên khách hàng:", font=self.bold_font).pack(side="left", padx=(0, 5))
        self.verify_customer_name_entry = ttk.Entry(customer_frame, font=self.base_font, width=30)
        self.verify_customer_name_entry.insert(0, "Chọn khách hàng")
        self.verify_customer_name_entry.configure(state="readonly")
        self.verify_customer_name_entry.pack(side="left", padx=(0, 5))

        def show_verify_customer_list():
            # Chỉ cho phép mở một cửa sổ duy nhất
            if self.verify_customer_window is not None and self.verify_customer_window.winfo_exists():
                self.verify_customer_window.lift()
                return

            self.verify_customer_window = tk.Toplevel(self.root)
            self.verify_customer_window.title("Chọn khách hàng")
            self.verify_customer_window.geometry("600x400")
            self.verify_customer_window.grab_set()

            self.verify_customer_window.protocol("WM_DELETE_WINDOW", lambda: on_verify_customer_window_close())

            def on_verify_customer_window_close():
                self.verify_customer_window.grab_release()
                self.verify_customer_window.destroy()
                self.verify_customer_window = None

            # Tìm kiếm khách hàng
            search_frame = ttk.Frame(self.verify_customer_window)
            search_frame.pack(fill="x", padx=5, pady=5)
            ttk.Label(search_frame, text="Tìm theo CCCD:", font=self.base_font).pack(side="left")
            search_entry = ttk.Entry(search_frame, font=self.base_font)
            search_entry.pack(side="left", padx=5, fill="x", expand=True)

            # Bảng khách hàng
            columns = ("MKH","CCCD", "Name", "Status")
            tree = ttk.Treeview(self.verify_customer_window, columns=columns, show="headings", height=10)
            tree.heading("MKH", text="Mã KH")
            tree.heading("CCCD", text="Số CCCD")
            tree.heading("Name", text="Họ và tên")
            tree.heading("Status", text="Trạng thái")
            tree.column("MKH", width=150, anchor="center")
            tree.column("CCCD", width=150, anchor="center")
            tree.column("Name", width=200, anchor="w")
            tree.column("Status", width=100, anchor="center")
            tree.pack(fill="both", expand=True, padx=5, pady=5)

            item_to_mkh = {}

            def populate_list(search_text=""):
                for item in tree.get_children():
                    tree.delete(item)
                item_to_mkh.clear()
                for customer in self.khach_hang_bus.get_khach_hang_all():
                    if search_text.lower() in customer.CCCD.lower():
                        status = "Hoạt động" if customer.TT == 1 else "Bị khóa" if customer.TT == 0 else "Chưa kích hoạt"
                        item_id = tree.insert("", "end", values=(customer.MKH, customer.CCCD, customer.HOTEN, status))
                        item_to_mkh[item_id] = customer.MKH

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
                mkh = item_to_mkh.get(item_id)
                customer = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(int(mkh))
                if customer:
                    self.verify_customer_id = str(customer.MKH)
                    self.verify_customer_name_entry.configure(state="normal")
                    self.verify_customer_name_entry.delete(0, "end")
                    self.verify_customer_name_entry.insert(0, customer.HOTEN)
                    self.verify_customer_name_entry.configure(state="readonly")
                    on_verify_customer_window_close()

            ttk.Button(self.verify_customer_window, text="Chọn", command=select_customer).pack(pady=10)

        ttk.Button(customer_frame, text="...", width=5, command=show_verify_customer_list).pack(side="left")

        # Chọn và hiển thị ảnh chữ ký
        ttk.Label(frame_verify, text="Ảnh chữ ký:", font=self.bold_font).pack(anchor="w", padx=5, pady=5)
        self.signature_label = ttk.Label(frame_verify, text="Chưa có ảnh chữ ký được chọn", font=self.base_font)
        self.signature_label.pack(fill="x", padx=5, pady=5)

        button_frame = ttk.Frame(frame_verify)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Chọn ảnh chữ ký", command=self.select_signature_to_verify).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xác nhận", command=self.verify_signature).pack(side="right", padx=5)

        self.verify_customer_id = None

    def refresh_customer_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        inactive_customers = [kh for kh in self.khach_hang_bus.get_khach_hang_all() if kh.TT == 2]
        
        for customer in inactive_customers:
            self.tree.insert("", "end", values=(customer.MKH, customer.CCCD, customer.HOTEN))

    def refresh_verify_customer_list(self):
        # Không cần thiết vì đã sử dụng cửa sổ chọn khách hàng
        pass

    def add_signature_images(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng trước!")
            return
        
        files = filedialog.askopenfilenames(
            title="Chọn ảnh chữ ký",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        for file in files:
            self.selected_images.append(file)
            self.image_listbox.insert(tk.END, os.path.basename(file))
        
        if len(self.selected_images) < 3:
            messagebox.showinfo("Thông báo", f"Đã chọn {len(self.selected_images)} ảnh. Cần ít nhất 3 ảnh chữ ký mẫu.")

    def save_signatures(self):
        global model, label_to_index, index_to_label
        
        if not self.selected_customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng trước!")
            return
        
        if len(self.selected_images) < 3:
            messagebox.showwarning("Cảnh báo", f"Chưa đủ chữ ký mẫu. Cần ít nhất 3 ảnh, hiện có: {len(self.selected_images)}")
            return
        
        customer_dir = os.path.join(new_customer_dir, self.selected_customer_id)
        os.makedirs(customer_dir, exist_ok=True)
        
        for img_path in self.selected_images:
            dest_path = os.path.join(customer_dir, os.path.basename(img_path))
            shutil.copy2(img_path, dest_path)
        
        reference_customer_path = os.path.join(reference_dir, self.selected_customer_id)
        shutil.move(customer_dir, reference_customer_path)
        
        kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(int(self.selected_customer_id))
        if not kh:
            messagebox.showerror("Lỗi", f"Không tìm thấy khách hàng với ID: {self.selected_customer_id}")
            return
        
        original_tt = kh.TT
        kh.TT = 1
        self.khach_hang_bus.update_khach_hang(kh)
        
        result = train_vgg16_model()
        if result[0] is None:
            kh.TT = original_tt
            self.khach_hang_bus.update_khach_hang(kh)
            messagebox.showwarning("Cảnh báo", "Không thể huấn luyện mô hình vì không có dữ liệu.")
            return
        
        kh.TT = original_tt
        self.khach_hang_bus.update_khach_hang(kh)
        
        model, label_to_index, index_to_label = result
        
        messagebox.showinfo("Thành công", f"Đã thêm chữ ký mẫu cho khách hàng {self.selected_customer_id} với {len(self.selected_images)} chữ ký mẫu.")
        
        self.selected_customer_id = None
        self.customer_name_entry.configure(state="normal")
        self.customer_name_entry.delete(0, "end")
        self.customer_name_entry.insert(0, "Chọn khách hàng")
        self.customer_name_entry.configure(state="readonly")
        self.selected_images = []
        self.image_listbox.delete(0, tk.END)
        self.refresh_customer_list()

    def select_signature_to_verify(self):
        file = filedialog.askopenfilename(
            title="Chọn ảnh chữ ký",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file:
            # Đảm bảo thư mục current_dir tồn tại
            if not os.path.exists(current_dir):
                os.makedirs(current_dir, exist_ok=True)
                
            dest_path = os.path.join(current_dir, "current_signature.jpg")
            shutil.copy2(file, dest_path)
            self.signature_label.config(text=f"Đã chọn: {os.path.basename(file)}")
            
            img = Image.open(file)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.signature_label.config(image=photo, text="")
            self.signature_label.image = photo

    def verify_signature(self):
        if not self.verify_customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return
        
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
        
        entropy = calculate_entropy(predictions[0])
        entropy_threshold = 0.6
        
        predicted_customer_dir = os.path.join(reference_dir, predicted_mkh)
        sample_image_path = None
        if os.path.exists(predicted_customer_dir):
            for file in os.listdir(predicted_customer_dir):
                if file.lower().endswith(image_extensions):
                    sample_image_path = os.path.join(predicted_customer_dir, file)
                    break
        
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(load_img(current_signature_path))
        plt.title("Chữ ký hiện tại")
        plt.axis('off')
        
        if sample_image_path:
            plt.subplot(1, 2, 2)
            plt.imshow(load_img(sample_image_path))
            plt.title(f"Chữ ký mẫu của MKH: {predicted_mkh}\nConfidence: {confidence:.4f}")
            plt.axis('off')
        
        plt.show()
        
        threshold = 0.8
        if confidence < threshold or entropy > entropy_threshold:
            messagebox.showwarning("Kết quả", f"Chữ ký không đủ độ tin cậy để xác thực.\nConfidence: {confidence:.4f}\nEntropy: {entropy:.4f}")
        elif predicted_mkh == self.verify_customer_id:
            messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {self.verify_customer_id}\nConfidence: {confidence:.4f}")
            
            kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(int(self.verify_customer_id))
            if kh:
                if kh.TT in [0, 2]:
                    kh.TT = 1
                    self.khach_hang_bus.update_khach_hang(kh)
                    status_message = "kích hoạt lại" if kh.TT == 0 else "kích hoạt"
                    print(f"Đã {status_message} khách hàng {self.verify_customer_id} thành trạng thái Hoạt động.")
                else:
                    print(f"Khách hàng {self.verify_customer_id} đã ở trạng thái Hoạt động.")
            else:
                print(f"Không tìm thấy khách hàng với ID: {self.verify_customer_id}")
        else:
            messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {self.verify_customer_id}\nTrùng khớp với MKH: {predicted_mkh}\nConfidence: {confidence:.4f}")
        
        # Reset sau khi xác thực
        self.verify_customer_id = None
        self.verify_customer_name_entry.configure(state="normal")
        self.verify_customer_name_entry.delete(0, "end")
        self.verify_customer_name_entry.insert(0, "Chọn khách hàng")
        self.verify_customer_name_entry.configure(state="readonly")
        self.signature_label.config(image="", text="Chưa có ảnh chữ ký được chọn")