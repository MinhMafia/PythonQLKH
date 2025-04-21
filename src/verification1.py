import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
import matplotlib.pyplot as plt
import faiss
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from tensorflow.keras.layers import Flatten
from PIL import Image, ImageTk
from DTO.KhanhHangDTO import KhachHangDTO
from config.DatabaseManager import DatabaseManager
import cv2  # Thêm OpenCV để xử lý ảnh



# Đường dẫn gốc của dự án
base_dir = r"D:\Code\Py"

# Đường dẫn đến các thư mục
reference_dir = os.path.join(base_dir, "Signatures", "Reference")
current_dir = os.path.join(base_dir, "Signatures", "Current")
new_customer_dir = os.path.join(base_dir, "Signatures", "new_customer")

# Định dạng file hình ảnh được hỗ trợ
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Kết nối với database MySQL
db_manager = DatabaseManager()
conn = db_manager.get_connection()
cursor = conn.cursor(dictionary=True)

# Chuẩn bị mô hình trích xuất đặc trưng
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(200, 200, 3))
x = base_model.output
x = Flatten()(x)
feature_extractor = Model(inputs=base_model.input, outputs=x)
for layer in base_model.layers:
    layer.trainable = False

# Hàm trích xuất đặc trưng
def extract_features(image_path, model):
    img = load_img(image_path, target_size=(200, 200))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = model.predict(img_array)
    return features.flatten()

# Hàm tiền xử lý ảnh
def preprocess_signature_image(image_path):
    # Đọc ảnh
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    
    # 1. Resize ảnh
    target_size = (300, 300)
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    
    # 2. Chuyển sang thang xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Lọc nhiễu bằng Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 4. Làm nổi bật nét chữ ký bằng adaptive thresholding
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # 5. Lọc nhiễu thêm bằng morphological operations
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # 6. Phát hiện vùng chữ ký (dựa trên contours)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Không tìm thấy vùng chữ ký trong ảnh.")
    
    # Lấy bounding box của vùng chữ ký lớn nhất
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)
    
    # Cắt vùng chữ ký
    signature_region = cleaned[y:y+h, x:x+w]
    
    # 7. Đưa vùng chữ ký vào giữa khung ảnh
    output_size = target_size
    result = np.ones(output_size, dtype=np.uint8) * 255  # Nền trắng
    sig_h, sig_w = signature_region.shape
    
    # Tính vị trí để đặt chữ ký vào giữa
    start_x = (output_size[0] - sig_w) // 2
    start_y = (output_size[1] - sig_h) // 2
    end_x = start_x + sig_w
    end_y = start_y + sig_h
    
    # Đặt vùng chữ ký vào giữa
    result[start_y:end_y, start_x:end_x] = signature_region
    
    return result

# Khởi tạo FAISS index
customer_ids = [d for d in os.listdir(reference_dir) if os.path.isdir(os.path.join(reference_dir, d))]
customer_to_index = {cid: idx for idx, cid in enumerate(customer_ids)}
signature_paths = []
signature_customer_ids = []
features_list = []

# Đồng bộ với database: Chỉ lấy khách hàng có TT = 1 (active)
active_customers = []
for cid in customer_ids:
    cursor.execute("SELECT TT FROM KHACHHANG WHERE MKH = %s", (cid,))
    result = cursor.fetchone()
    if result and result['TT'] == 1:
        active_customers.append(cid)
customer_ids = active_customers
customer_to_index = {cid: idx for idx, cid in enumerate(customer_ids)}

# Trích xuất đặc trưng từ tất cả chữ ký mẫu
for customer_id in customer_ids:
    customer_dir = os.path.join(reference_dir, customer_id)
    for file in os.listdir(customer_dir):
        if file.lower().endswith(image_extensions):
            image_path = os.path.join(customer_dir, file)
            features = extract_features(image_path, feature_extractor)
            features_list.append(features)
            signature_paths.append(image_path)
            signature_customer_ids.append(customer_id)

features_array = np.array(features_list, dtype=np.float32)
dimension = features_array.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(features_array)
print(f"Đã thêm {index.ntotal} chữ ký mẫu vào FAISS index.")

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
        self.preprocessed_images = []  # Lưu đường dẫn ảnh đã tiền xử lý

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
        
        # Làm mới danh sách khách hàng active
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
        self.preprocessed_images = []
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
        
        # Tiền xử lý từng ảnh
        for file in files:
            try:
                # Tiền xử lý ảnh
                processed_img = preprocess_signature_image(file)
                
                # Tạo thư mục tạm để lưu ảnh đã tiền xử lý
                temp_dir = os.path.join(base_dir, "Signatures", "temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Lưu ảnh đã tiền xử lý
                processed_path = os.path.join(temp_dir, f"processed_{os.path.basename(file)}")
                cv2.imwrite(processed_path, processed_img)
                
                # Lưu vào danh sách
                self.selected_images.append(file)  # Lưu đường dẫn gốc để hiển thị
                self.preprocessed_images.append(processed_path)  # Lưu đường dẫn ảnh đã xử lý
                self.image_listbox.insert(tk.END, os.path.basename(file))
            except Exception as e:
                messagebox.showwarning("Cảnh báo", f"Lỗi khi tiền xử lý ảnh {os.path.basename(file)}: {str(e)}")
                continue
        
        if len(self.selected_images) < 3:
            messagebox.showinfo("Thông báo", f"Đã chọn {len(self.selected_images)} ảnh. Cần ít nhất 3 ảnh chữ ký mẫu.")

    def save_signatures(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng trước!")
            return
        
        if len(self.selected_images) < 3:
            messagebox.showwarning("Cảnh báo", f"Chưa đủ chữ ký mẫu. Cần ít nhất 3 ảnh, hiện có: {len(self.selected_images)}")
            return
        
        # Tạo thư mục cho khách hàng mới trong new_customer
        customer_dir = os.path.join(new_customer_dir, self.selected_customer_id)
        os.makedirs(customer_dir, exist_ok=True)
        
        # Sao chép ảnh đã tiền xử lý vào thư mục new_customer
        for processed_path in self.preprocessed_images:
            dest_path = os.path.join(customer_dir, os.path.basename(processed_path))
            shutil.copy2(processed_path, dest_path)
        
        # Xóa thư mục tạm
        temp_dir = os.path.join(base_dir, "Signatures", "temp")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # Trích xuất đặc trưng
        new_features = []
        temp_paths = []
        new_customer_ids_list = []
        for file in os.listdir(customer_dir):
            if file.lower().endswith(image_extensions):
                image_path = os.path.join(customer_dir, file)
                features = extract_features(image_path, feature_extractor)
                new_features.append(features)
                temp_paths.append(image_path)
                new_customer_ids_list.append(self.selected_customer_id)
        
        # Di chuyển thư mục vào Reference
        reference_customer_path = os.path.join(reference_dir, self.selected_customer_id)
        shutil.move(customer_dir, reference_customer_path)
        
        # Cập nhật đường dẫn
        new_paths = []
        for temp_path in temp_paths:
            file_name = os.path.basename(temp_path)
            new_path = os.path.join(reference_customer_path, file_name)
            new_paths.append(new_path)
        
        # Thêm vào FAISS index
        new_features_array = np.array(new_features, dtype=np.float32)
        index.add(new_features_array)
        
        # Cập nhật danh sách thông tin
        signature_paths.extend(new_paths)
        signature_customer_ids.extend(new_customer_ids_list)
        customer_ids.append(self.selected_customer_id)
        customer_to_index[self.selected_customer_id] = len(customer_ids) - 1
        
        # Kích hoạt khách hàng trong database
        cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (self.selected_customer_id,))
        conn.commit()
        
        messagebox.showinfo("Thành công", f"Đã kích hoạt khách hàng {self.selected_customer_id} với {len(new_features)} chữ ký mẫu.")
        
        # Làm mới danh sách
        self.refresh_customer_list()
        self.refresh_verify_customer_list()
        self.selected_images = []
        self.preprocessed_images = []
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
        
        # Trích xuất đặc trưng từ chữ ký hiện tại
        current_features = extract_features(current_signature_path, feature_extractor)
        
        # Tìm kiếm chữ ký mẫu gần nhất bằng FAISS
        k = 1
        current_features = np.array([current_features], dtype=np.float32)
        distances, indices = index.search(current_features, k)
        
        # Lấy thông tin chữ ký mẫu gần nhất
        best_match_index = indices[0][0]
        best_match_distance = distances[0][0]
        best_match_path = signature_paths[best_match_index]
        best_match_customer = signature_customer_ids[best_match_index]
        
        # Tính độ tương đồng
        max_distance = 1e6
        similarity = 1 - (best_match_distance / max_distance)
        if similarity < 0:
            similarity = 0
        
        # Hiển thị kết quả
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(load_img(current_signature_path))
        plt.title("Chữ ký hiện tại")
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(load_img(best_match_path))
        plt.title(f"Chữ ký mẫu của MKH: {best_match_customer}\nSimilarity: {similarity:.4f}")
        plt.axis('off')
        plt.show()
        
        # Xác thực
        threshold = 0.9
        if best_match_customer == customer_id and similarity >= threshold:
            messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {customer_id}\nĐộ tương đồng: {similarity:.4f}")
            # Cập nhật trạng thái khách hàng
            cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (customer_id,))
            conn.commit()
        else:
            messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {customer_id}\nTrùng khớp với MKH: {best_match_customer}\nĐộ tương đồng: {similarity:.4f}")

# Chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = SignatureVerificationApp(root)
    root.mainloop()

# Đóng kết nối database
db_manager.close_connection(conn)