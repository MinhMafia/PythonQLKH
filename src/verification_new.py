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
unknown_dir = os.path.join(base_dir, "Signatures", "unknown")  # Thư mục cho dữ liệu âm
model_dir = os.path.join(base_dir, "Models")
os.makedirs(model_dir, exist_ok=True)
os.makedirs(unknown_dir, exist_ok=True)
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
    
    # Thêm lớp "unknown"
    classes = eligible_customers + ['unknown']
    
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
    
    # Tải dữ liệu từ lớp "unknown"
    for file in os.listdir(unknown_dir):
        if file.lower().endswith(image_extensions):
            image_path = os.path.join(unknown_dir, file)
            img = load_img(image_path, target_size=(200, 200))
            img_array = img_to_array(img)
            img_array = preprocess_input(img_array)
            X.append(img_array)
            y.append(label_to_index['unknown'])
    
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
    train_generator = datagen.flow(X_train, y_train, batch_size=32)
    
    # Không tăng cường dữ liệu cho tập kiểm tra
    val_datagen = ImageDataGenerator()
    val_generator = val_datagen.flow(X_val, y_val, batch_size=32)
    
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
    
    # Huấn luyện mô hình
    model.fit(
        train_generator,
        epochs=15,  # Tăng số epochs
        steps_per_epoch=len(X_train) // 32,
        validation_data=val_generator,
        validation_steps=len(X_val) // 32,
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
    
    classes = eligible_customers + ['unknown']
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

        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        
        # Tab 1: Thêm chữ ký mẫu
        self.tab_add_customer = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_add_customer, text="Thêm chữ ký mẫu")
        
        # Tab 2: Xác thực chữ ký
        self.tab_verify = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_verify, text="Xác thực chữ ký")
        
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_add_customer_tab()
        self.setup_verify_tab()
        
        # Danh sách ảnh tạm thời cho khách hàng mới
        self.selected_images = []
        self.selected_customer_id = None

    def setup_add_customer_tab(self):
        frame_list = ttk.LabelFrame(self.tab_add_customer, text="Khách hàng chưa kích hoạt")
        frame_list.pack(padx=10, pady=5, fill="x")
        
        self.tree = ttk.Treeview(frame_list, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="Mã khách hàng")
        self.tree.heading("Name", text="Họ và tên")
        self.tree.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(frame_list, text="Làm mới", command=self.refresh_customer_list).pack(pady=5)
        
        frame_add = ttk.LabelFrame(self.tab_add_customer, text="Thêm chữ ký mẫu")
        frame_add.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(frame_add, text="Chọn khách hàng:").pack(anchor="w", padx=5)
        self.customer_var = tk.StringVar()
        self.customer_dropdown = ttk.Combobox(frame_add, textvariable=self.customer_var, state="readonly")
        self.customer_dropdown.pack(fill="x", padx=5, pady=2)
        self.customer_dropdown.bind("<<ComboboxSelected>>", self.on_customer_select)
        
        ttk.Button(frame_add, text="Thêm ảnh chữ ký", command=self.add_signature_images).pack(pady=5)
        
        self.image_listbox = tk.Listbox(frame_add, height=5)
        self.image_listbox.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(frame_add, text="Lưu trữ", command=self.save_signatures).pack(pady=5)
        
        self.refresh_customer_list()

    def setup_verify_tab(self):
        frame_verify = ttk.LabelFrame(self.tab_verify, text="Xác thực chữ ký khách hàng")
        frame_verify.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(frame_verify, text="Chọn khách hàng:").pack(anchor="w", padx=5)
        self.verify_customer_var = tk.StringVar()
        self.verify_customer_dropdown = ttk.Combobox(frame_verify, textvariable=self.verify_customer_var, state="readonly")
        self.verify_customer_dropdown.pack(fill="x", padx=5, pady=2)
        
        ttk.Button(frame_verify, text="Chọn ảnh chữ ký", command=self.select_signature_to_verify).pack(pady=5)
        
        self.signature_label = ttk.Label(frame_verify, text="Chưa có ảnh chữ ký được chọn")
        self.signature_label.pack(pady=5)
        
        ttk.Button(frame_verify, text="Xác nhận", command=self.verify_signature).pack(pady=5)
        
        self.refresh_verify_customer_list()

    def refresh_customer_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        inactive_customers = [kh for kh in self.khach_hang_bus.get_khach_hang_all() if kh.TT == 2]
        
        for customer in inactive_customers:
            self.tree.insert("", "end", values=(customer.MKH, customer.HOTEN))
        
        self.customer_dropdown['values'] = [str(customer.MKH) for customer in inactive_customers]

    def refresh_verify_customer_list(self):
        all_customers = self.khach_hang_bus.get_khach_hang_all()
        self.verify_customer_dropdown['values'] = [str(customer.MKH) for customer in all_customers]

    def on_customer_select(self, event):
        self.selected_customer_id = self.customer_var.get()
        self.selected_images = []
        self.image_listbox.delete(0, tk.END)
        messagebox.showinfo("Thông báo", f"Đã chọn khách hàng {self.selected_customer_id}. Vui lòng thêm ít nhất 3 ảnh chữ ký mẫu.")

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
        
        # Tạo thư mục cho khách hàng mới trong new_customer
        customer_dir = os.path.join(new_customer_dir, self.selected_customer_id)
        os.makedirs(customer_dir, exist_ok=True)
        
        # Sao chép ảnh vào thư mục new_customer
        for img_path in self.selected_images:
            dest_path = os.path.join(customer_dir, os.path.basename(img_path))
            shutil.copy2(img_path, dest_path)
        
        # Di chuyển thư mục vào Reference
        reference_customer_path = os.path.join(reference_dir, self.selected_customer_id)
        shutil.move(customer_dir, reference_customer_path)
        
        # Tạm thời cập nhật trạng thái khách hàng để huấn luyện
        kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(int(self.selected_customer_id))
        if not kh:
            messagebox.showerror("Lỗi", f"Không tìm thấy khách hàng với ID: {self.selected_customer_id}")
            return
        
        original_tt = kh.TT  # Lưu trạng thái gốc
        kh.TT = 1  # Tạm thời đặt TT = 1 để huấn luyện
        self.khach_hang_bus.update_khach_hang(kh)
        
        # Huấn luyện lại mô hình với dữ liệu mới
        result = train_vgg16_model()
        if result[0] is None:
            # Khôi phục trạng thái nếu huấn luyện thất bại
            kh.TT = original_tt
            self.khach_hang_bus.update_khach_hang(kh)
            messagebox.showwarning("Cảnh báo", "Không thể huấn luyện mô hình vì không có dữ liệu.")
            return
        
        # Khôi phục trạng thái gốc sau khi huấn luyện
        kh.TT = original_tt
        self.khach_hang_bus.update_khach_hang(kh)
        
        model, label_to_index, index_to_label = result
        
        messagebox.showinfo("Thành công", f"Đã thêm chữ ký mẫu cho khách hàng {self.selected_customer_id} với {len(self.selected_images)} chữ ký mẫu.")
        
        self.refresh_customer_list()
        self.refresh_verify_customer_list()
        self.selected_images = []
        self.image_listbox.delete(0, tk.END)

    def select_signature_to_verify(self):
        file = filedialog.askopenfilename(
            title="Chọn ảnh chữ ký",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file:
            dest_path = os.path.join(current_dir, "current_signature.jpg")
            shutil.copy2(file, dest_path)
            self.signature_label.config(text=f"Đã chọn: {os.path.basename(file)}")
            
            img = Image.open(file)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.signature_label.config(image=photo, text="")
            self.signature_label.image = photo

    def verify_signature(self):
        customer_id = self.verify_customer_var.get()
        if not customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return
        
        current_signature_path = os.path.join(current_dir, "current_signature.jpg")
        if not os.path.exists(current_signature_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh chữ ký!")
            return
        
        if not model:
            messagebox.showerror("Lỗi", "Không có mô hình để xác thực. Vui lòng huấn luyện mô hình trước.")
            return
        
        # Chuẩn bị ảnh chữ ký hiện tại
        img = load_img(current_signature_path, target_size=(200, 200))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Dự đoán khách hàng
        predictions = model.predict(img_array)
        predicted_label = np.argmax(predictions, axis=1)[0]
        predicted_mkh = index_to_label.get(predicted_label, "Không xác định")
        confidence = predictions[0][predicted_label]
        
        # Tính entropy để kiểm tra độ không chắc chắn
        entropy = calculate_entropy(predictions[0])
        entropy_threshold = 0.6
        
        # Tìm ảnh mẫu của khách hàng dự đoán
        predicted_customer_dir = os.path.join(reference_dir, predicted_mkh) if predicted_mkh != 'unknown' else unknown_dir
        sample_image_path = None
        if os.path.exists(predicted_customer_dir):
            for file in os.listdir(predicted_customer_dir):
                if file.lower().endswith(image_extensions):
                    sample_image_path = os.path.join(predicted_customer_dir, file)
                    break
        
        # Hiển thị kết quả
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(load_img(current_signature_path))
        plt.title("Chữ ký hiện tại")
        plt.axis('off')
        
        if sample_image_path:
            plt.subplot(1, 2, 2)
            plt.imshow(load_img(sample_image_path))
            plt.title(f"Chữ ký mẫu của {'MKH: ' + predicted_mkh if predicted_mkh != 'unknown' else 'unknown'}\nConfidence: {confidence:.4f}")
            plt.axis('off')
        
        # plt.savefig('signature_comparison.png')
        # plt.close()
        plt.show()
        
        # Xác thực
        threshold = 0.8  # Tăng ngưỡng để yêu cầu độ tin cậy cao hơn
        if predicted_mkh == 'unknown':
            messagebox.showwarning("Kết quả", f"Chữ ký không khớp với bất kỳ khách hàng nào (unknown).\nConfidence: {confidence:.4f}")
        elif predicted_mkh == customer_id and confidence >= threshold and entropy < entropy_threshold:
            messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {customer_id}\nConfidence: {confidence:.4f}")
            
            kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(int(customer_id))
            if kh:
                if kh.TT in [0, 2]:
                    kh.TT = 1
                    self.khach_hang_bus.update_khach_hang(kh)
                    status_message = "kích hoạt lại" if kh.TT == 0 else "kích hoạt"
                    print(f"Đã {status_message} khách hàng {customer_id} thành trạng thái Hoạt động.")
                else:
                    print(f"Khách hàng {customer_id} đã ở trạng thái Hoạt động.")
            else:
                print(f"Không tìm thấy khách hàng với ID: {customer_id}")
        else:
            messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {customer_id}\nTrùng khớp với {'MKH: ' + predicted_mkh if predicted_mkh != 'unknown' else 'unknown'}\nConfidence: {confidence:.4f}")