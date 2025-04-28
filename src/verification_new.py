import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, Flatten, Input
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

from DTO.KhanhHangDTO import KhachHangDTO
from config.DatabaseManager import DatabaseManager
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
model_path = os.path.join(model_dir, "signature_model.keras")  # Sử dụng định dạng .keras

# Định dạng file hình ảnh được hỗ trợ
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Kết nối với database MySQL
db_manager = DatabaseManager()
conn = db_manager.get_connection()
cursor = conn.cursor(dictionary=True)

# Hàm huấn luyện mô hình VGG16 với tăng cường dữ liệu
def train_vgg16_model():
    # Lấy danh sách khách hàng đã kích hoạt
    cursor.execute("SELECT MKH FROM KHACHHANG WHERE TT = 1")
    active_customers = [str(customer['MKH']) for customer in cursor.fetchall()]
    
    if not active_customers:
        print("Không có khách hàng nào để huấn luyện mô hình.")
        return None, None, None  # Trả về 3 giá trị None
    
    # Chuẩn bị dữ liệu huấn luyện
    X = []
    y = []
    label_to_index = {str(mkh): idx for idx, mkh in enumerate(active_customers)}
    index_to_label = {idx: mkh for mkh, idx in label_to_index.items()}
    
    # Tải dữ liệu gốc
    for mkh in active_customers:
        customer_dir = os.path.join(reference_dir, str(mkh))
        for file in os.listdir(customer_dir):
            if file.lower().endswith(image_extensions):
                image_path = os.path.join(customer_dir, file)
                img = load_img(image_path, target_size=(200, 200))
                img_array = img_to_array(img)
                img_array = preprocess_input(img_array)
                X.append(img_array)
                y.append(label_to_index[str(mkh)])
    
    X = np.array(X)
    y = np.array(y)
    y = tf.keras.utils.to_categorical(y, num_classes=len(active_customers))
    
    # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Tăng cường dữ liệu bằng ImageDataGenerator
    datagen = ImageDataGenerator(
        rotation_range=20,           # Xoay ngẫu nhiên trong khoảng ±20 độ
        width_shift_range=0.1,      # Dịch chuyển ngang ±10%
        height_shift_range=0.1,     # Dịch chuyển dọc ±10%
        brightness_range=[0.8, 1.2],# Thay đổi độ sáng từ 80% đến 120%
        zoom_range=0.2,             # Thu phóng ±20%
        horizontal_flip=False,      # Không lật ngang (chữ ký thường có hướng cố định)
        fill_mode='nearest'         # Điền các khoảng trống bằng giá trị gần nhất
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
    predictions = Dense(len(active_customers), activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Biên dịch mô hình
    model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Huấn luyện mô hình
    model.fit(
        train_generator,
        epochs=10,
        steps_per_epoch=len(X_train) // 32,
        validation_data=val_generator,
        validation_steps=len(X_val) // 32,
        verbose=1
    )
    
    # Lưu mô hình với định dạng .keras
    model.save(model_path)
    print(f"Đã huấn luyện và lưu mô hình tại {model_path}")
    
    return model, label_to_index, index_to_label  # Trả về 3 giá trị

# Tải mô hình và danh sách nhãn
def load_model_and_labels():
    cursor.execute("SELECT MKH FROM KHACHHANG WHERE TT = 1")
    active_customers = [str(customer['MKH']) for customer in cursor.fetchall()]
    label_to_index = {str(mkh): idx for idx, mkh in enumerate(active_customers)}
    index_to_label = {idx: mkh for mkh, idx in label_to_index.items()}
    
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
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống xác thực chữ ký khách hàng")

        # Tab control
        self.tab_control = ttk.Notebook(root)
        
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
        # Frame danh sách khách hàng chưa kích hoạt
        frame_list = ttk.LabelFrame(self.tab_add_customer, text="Khách hàng chưa kích hoạt")
        frame_list.pack(padx=10, pady=5, fill="x")
        
        self.tree = ttk.Treeview(frame_list, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="Mã khách hàng")
        self.tree.heading("Name", text="Họ và tên")
        self.tree.pack(fill="x", padx=5, pady=5)
        
        # Nút làm mới danh sách
        ttk.Button(frame_list, text="Làm mới", command=self.refresh_customer_list).pack(pady=5)
        
        # Frame thêm chữ ký mẫu
        frame_add = ttk.LabelFrame(self.tab_add_customer, text="Thêm chữ ký mẫu")
        frame_add.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(frame_add, text="Chọn khách hàng:").pack(anchor="w", padx=5)
        self.customer_var = tk.StringVar()
        self.customer_dropdown = ttk.Combobox(frame_add, textvariable=self.customer_var, state="readonly")
        self.customer_dropdown.pack(fill="x", padx=5, pady=2)
        self.customer_dropdown.bind("<<ComboboxSelected>>", self.on_customer_select)
        
        ttk.Button(frame_add, text="Thêm ảnh chữ ký", command=self.add_signature_images).pack(pady=5)
        
        # Hiển thị danh sách ảnh đã chọn
        self.image_listbox = tk.Listbox(frame_add, height=5)
        self.image_listbox.pack(fill="x", padx=5, pady=5)
        
        # Nút lưu trữ
        ttk.Button(frame_add, text="Lưu trữ", command=self.save_signatures).pack(pady=5)
        
        # Làm mới danh sách khi khởi động
        self.refresh_customer_list()

    def setup_verify_tab(self):
        # Frame xác thực chữ ký
        frame_verify = ttk.LabelFrame(self.tab_verify, text="Xác thực chữ ký khách hàng")
        frame_verify.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(frame_verify, text="Chọn khách hàng:").pack(anchor="w", padx=5)
        self.verify_customer_var = tk.StringVar()
        self.verify_customer_dropdown = ttk.Combobox(frame_verify, textvariable=self.verify_customer_var, state="readonly")
        self.verify_customer_dropdown.pack(fill="x", padx=5, pady=2)
        
        ttk.Button(frame_verify, text="Chọn ảnh chữ ký", command=self.select_signature_to_verify).pack(pady=5)
        
        # Hiển thị ảnh đã chọn
        self.signature_label = ttk.Label(frame_verify, text="Chưa có ảnh chữ ký được chọn")
        self.signature_label.pack(pady=5)
        
        # Nút xác nhận
        ttk.Button(frame_verify, text="Xác nhận", command=self.verify_signature).pack(pady=5)
        
        # Làm mới danh sách khách hàng
        self.refresh_verify_customer_list()

    def refresh_customer_list(self):
        # Xóa danh sách hiện tại
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách khách hàng chưa kích hoạt
        cursor.execute("SELECT MKH, HOTEN FROM KHACHHANG WHERE TT = 0")
        inactive_customers = cursor.fetchall()
        
        # Thêm vào treeview
        for customer in inactive_customers:
            self.tree.insert("", "end", values=(customer['MKH'], customer['HOTEN']))
        
        # Cập nhật combobox
        self.customer_dropdown['values'] = [str(customer['MKH']) for customer in inactive_customers]

    def refresh_verify_customer_list(self):
        # Lấy danh sách tất cả khách hàng để xác thực
        cursor.execute("SELECT MKH FROM KHACHHANG")
        all_customers = cursor.fetchall()
        self.verify_customer_dropdown['values'] = [str(customer['MKH']) for customer in all_customers]

    def on_customer_select(self, event):
        self.selected_customer_id = self.customer_var.get()
        self.selected_images = []
        self.image_listbox.delete(0, tk.END)
        messagebox.showinfo("Thông báo", f"Đã chọn khách hàng {self.selected_customer_id}. Vui lòng thêm ít nhất 3 ảnh chữ ký mẫu.")

    def add_signature_images(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng trước!")
            return
        
        # Chọn nhiều ảnh
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
        
        # Kích hoạt khách hàng trong database
        cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (self.selected_customer_id,))
        conn.commit()
        
        # Huấn luyện lại mô hình với dữ liệu mới
        result = train_vgg16_model()
        if result[0] is None:  # Kiểm tra nếu không có mô hình
            messagebox.showwarning("Cảnh báo", "Không thể huấn luyện mô hình vì không có khách hàng nào để huấn luyện.")
            return
        
        model, label_to_index, index_to_label = result
        
        messagebox.showinfo("Thành công", f"Đã kích hoạt khách hàng {self.selected_customer_id} với {len(self.selected_images)} chữ ký mẫu.")
        
        # Làm mới danh sách
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
            # Sao chép ảnh vào thư mục Current
            dest_path = os.path.join(current_dir, "current_signature.jpg")
            shutil.copy2(file, dest_path)
            self.signature_label.config(text=f"Đã chọn: {os.path.basename(file)}")
            
            # Hiển thị ảnh
            img = Image.open(file)
            img = img.resize((150, 150), Image.LANCZOS)
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
        predicted_mkh = index_to_label[predicted_label]
        confidence = predictions[0][predicted_label]
        
        # Tìm một ảnh mẫu của khách hàng dự đoán
        predicted_customer_dir = os.path.join(reference_dir, predicted_mkh)
        sample_image_path = None
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
            plt.title(f"Chữ ký mẫu của MKH: {predicted_mkh}\nConfidence: {confidence:.4f}")
            plt.axis('off')
        plt.show()
        
        # Xác thực
        threshold = 0.9
        if predicted_mkh == customer_id and confidence >= threshold:
            messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {customer_id}\nConfidence: {confidence:.4f}")
            cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (customer_id,))
            conn.commit()
        else:
            messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {customer_id}\nTrùng khớp với MKH: {predicted_mkh}\nConfidence: {confidence:.4f}")

# Chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = SignatureVerificationApp(root)
    root.mainloop()

# Đóng kết nối database
db_manager.close_connection(conn)