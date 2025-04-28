import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.layers import Flatten
import matplotlib.pyplot as plt
import faiss
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

from DTO.KhanhHangDTO import KhachHangDTO
from config.DatabaseManager import DatabaseManager
from BUS.KhachHangBUS import KhachHangBUS
from pathlib import Path 

# Đường dẫn gốc của dự án
currentDir = Path(__file__).parent
base_dir = currentDir.parent / "database" 
 

# Đường dẫn đến các thư mục
reference_dir = os.path.join(base_dir, "Signatures", "Reference")
current_dir = os.path.join(base_dir, "Signatures", "Current")
new_customer_dir = os.path.join(base_dir, "Signatures", "new_customer")

# Định dạng file hình ảnh được hỗ trợ
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Kết nối với database MySQL
# db_manager = DatabaseManager()
# conn = db_manager.get_connection()
# cursor = conn.cursor(dictionary=True)

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

# Khởi tạo FAISS index
customer_ids = [d for d in os.listdir(reference_dir) if os.path.isdir(os.path.join(reference_dir, d))]
customer_to_index = {cid: idx for idx, cid in enumerate(customer_ids)}
signature_paths = []
signature_customer_ids = []
features_list = []

# Đồng bộ với database: Chỉ lấy khách hàng có TT = 1 (active)
active_customers = []
# for cid in customer_ids:
#     cursor.execute("SELECT TT FROM KHACHHANG WHERE MKH = %s", (cid,))
#     result = cursor.fetchone()
#     if result and result['TT'] == 1:
#         active_customers.append(cid)
# Lọc ra những khách hàng có trạng thái TT = 1 (active)
active_customers = [kh.MKH for kh in KhachHangBUS().get_khach_hang_all() if kh.TT == 1 and os.path.exists(os.path.join(reference_dir, str(kh.MKH)))]
customer_ids = active_customers
customer_to_index = {cid: idx for idx, cid in enumerate(customer_ids)}

# Trích xuất đặc trưng từ tất cả chữ ký mẫu
for customer_id in customer_ids:
    customer_dir = os.path.join(reference_dir, str(customer_id))
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

# Giao diện đồ họa mới
class SignatureVerificationApp:
    # def __init__(self, root):
    #     self.root = root
    def __init__(self, parent_frame):
        self.root = parent_frame  # Sử dụng frame được truyền vào thay vì tạo cửa sổ mới
        # self.root.title("Hệ thống xác thực chữ ký khách hàng") #Ko hỗ trợ tiêu đề cho frame, khi tạo cửa sổ thì mới sài đc
        self.khach_hang_bus = KhachHangBUS()  # Khởi tạo BUS để giao tiếp với DAO

        # Tab control
        # self.tab_control = ttk.Notebook(root)
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
        
        # # Lấy danh sách khách hàng chưa kích hoạt
        # cursor.execute("SELECT MKH, HOTEN FROM KHACHHANG WHERE TT = 0")
        # inactive_customers = cursor.fetchall()

        # Lấy danh sách khách hàng chưa kích hoạt từ BUS
        inactive_customers = [kh for kh in self.khach_hang_bus.get_khach_hang_all() if kh.TT == 0]
        
        # Thêm vào treeview
        for customer in inactive_customers:
            self.tree.insert("", "end", values=(customer.MKH, customer.HOTEN))
        
        # Cập nhật combobox
        self.customer_dropdown['values'] = [str(customer.MKH) for customer in inactive_customers]

    def refresh_verify_customer_list(self):
        # # Lấy danh sách tất cả khách hàng để xác thực
        # cursor.execute("SELECT MKH FROM KHACHHANG")
        # all_customers = cursor.fetchall()
        # self.verify_customer_dropdown['values'] = [str(customer['MKH']) for customer in all_customers]
        # Lấy danh sách tất cả khách hàng từ BUS
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
        
        # # Kích hoạt khách hàng trong database
        # cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (self.selected_customer_id,))
        # conn.commit()

        # Kích hoạt khách hàng trong database thông qua BUS
        kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(self.selected_customer_id)
        # if kh:
        #     kh.TT = 1
        #     self.khach_hang_bus.update_khach_hang(kh)
        if kh:
            print(f"Đã tìm thấy khách hàng: {kh.MKH}, trạng thái hiện tại: {kh.TT}")
            kh.TT = 1
            self.khach_hang_bus.update_khach_hang(kh)
            print(f"Trạng thái mới: {kh.TT}")
        else:
            print(f"Không tìm thấy khách hàng với ID: {self.selected_customer_id}")
                
        messagebox.showinfo("Thành công", f"Đã kích hoạt khách hàng {self.selected_customer_id} với {len(new_features)} chữ ký mẫu.")
        
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
        threshold = 0.7 # Ngưỡng xác thực
        if best_match_customer == customer_id and similarity >= threshold:
            messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {customer_id}\nĐộ tương đồng: {similarity:.4f}")
            # Cập nhật trạng thái khách hàng thông qua BUS
            # kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(customer_id)
            # if kh:
            #     kh.TT = 1
            #     self.khach_hang_bus.update_khach_hang(kh)

            kh = self.khach_hang_bus.find_khach_hang_by_ma_khach_hang(self.selected_customer_id)
            if kh:
                print(f"Đã tìm thấy khách hàng: {kh.MKH}, trạng thái hiện tại: {kh.TT}")
                kh.TT = 1
                self.khach_hang_bus.update_khach_hang(kh)
                print(f"Trạng thái mới: {kh.TT}")
            else:
                print(f"Không tìm thấy khách hàng với ID: {self.selected_customer_id}")
                
        else:
            messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {customer_id}\nTrùng khớp với MKH: {best_match_customer}\nĐộ tương đồng: {similarity:.4f}")

# Chạy ứng dụng
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = SignatureVerificationApp(root)
#     root.mainloop()

def load_verification_interface(parent_frame):
    # Xóa nội dung cũ trong frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # # Tạo giao diện xác minh chữ ký trong frame được truyền vào
    # label = tk.Label(parent_frame, text="Xác Minh Chữ Ký", font=("Arial", 24))
    # label.pack(pady=20)

    # # Các thành phần giao diện khác (ví dụ: nút, danh sách, v.v.)
    # verify_button = tk.Button(parent_frame, text="Bắt đầu xác minh", command=lambda: print("Xác minh..."))
    # verify_button.pack(pady=10)

    # Tạo một instance của SignatureVerificationApp và truyền parent_frame làm root
    app = SignatureVerificationApp(parent_frame)

# Đóng kết nối database
# # db_manager.close_connection(conn)
# def close_database_connection():
#     if conn.is_connected():
#         db_manager.close_connection(conn)



# # Giao diện đồ họa cũ 
# class SignatureVerificationApp:
#     # def __init__(self, root):
#     #     self.root = root
#     def __init__(self, parent_frame):
#         self.root = parent_frame  # Sử dụng frame được truyền vào thay vì tạo cửa sổ mới
#         # self.root.title("Hệ thống xác thực chữ ký khách hàng") #Ko hỗ trợ tiêu đề cho frame, khi tạo cửa sổ thì mới sài đc

#         # Tab control
#         # self.tab_control = ttk.Notebook(root)
#         self.tab_control = ttk.Notebook(self.root)
        
#         # Tab 1: Thêm chữ ký mẫu
#         self.tab_add_customer = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_add_customer, text="Thêm chữ ký mẫu")
        
#         # Tab 2: Xác thực chữ ký
#         self.tab_verify = ttk.Frame(self.tab_control)
#         self.tab_control.add(self.tab_verify, text="Xác thực chữ ký")
        
#         self.tab_control.pack(expand=1, fill="both")
        
#         self.setup_add_customer_tab()
#         self.setup_verify_tab()
        
#         # Danh sách ảnh tạm thời cho khách hàng mới
#         self.selected_images = []
#         self.selected_customer_id = None

#     def setup_add_customer_tab(self):
#         # Frame danh sách khách hàng chưa kích hoạt
#         frame_list = ttk.LabelFrame(self.tab_add_customer, text="Khách hàng chưa kích hoạt")
#         frame_list.pack(padx=10, pady=5, fill="x")
        
#         self.tree = ttk.Treeview(frame_list, columns=("ID", "Name"), show="headings")
#         self.tree.heading("ID", text="Mã khách hàng")
#         self.tree.heading("Name", text="Họ và tên")
#         self.tree.pack(fill="x", padx=5, pady=5)
        
#         # Nút làm mới danh sách
#         ttk.Button(frame_list, text="Làm mới", command=self.refresh_customer_list).pack(pady=5)
        
#         # Frame thêm chữ ký mẫu
#         frame_add = ttk.LabelFrame(self.tab_add_customer, text="Thêm chữ ký mẫu")
#         frame_add.pack(padx=10, pady=5, fill="x")
        
#         ttk.Label(frame_add, text="Chọn khách hàng:").pack(anchor="w", padx=5)
#         self.customer_var = tk.StringVar()
#         self.customer_dropdown = ttk.Combobox(frame_add, textvariable=self.customer_var, state="readonly")
#         self.customer_dropdown.pack(fill="x", padx=5, pady=2)
#         self.customer_dropdown.bind("<<ComboboxSelected>>", self.on_customer_select)
        
#         ttk.Button(frame_add, text="Thêm ảnh chữ ký", command=self.add_signature_images).pack(pady=5)
        
#         # Hiển thị danh sách ảnh đã chọn
#         self.image_listbox = tk.Listbox(frame_add, height=5)
#         self.image_listbox.pack(fill="x", padx=5, pady=5)
        
#         # Nút lưu trữ
#         ttk.Button(frame_add, text="Lưu trữ", command=self.save_signatures).pack(pady=5)
        
#         # Làm mới danh sách khi khởi động
#         self.refresh_customer_list()

#     def setup_verify_tab(self):
#         # Frame xác thực chữ ký
#         frame_verify = ttk.LabelFrame(self.tab_verify, text="Xác thực chữ ký khách hàng")
#         frame_verify.pack(padx=10, pady=5, fill="x")
        
#         ttk.Label(frame_verify, text="Chọn khách hàng:").pack(anchor="w", padx=5)
#         self.verify_customer_var = tk.StringVar()
#         self.verify_customer_dropdown = ttk.Combobox(frame_verify, textvariable=self.verify_customer_var, state="readonly")
#         self.verify_customer_dropdown.pack(fill="x", padx=5, pady=2)
        
#         ttk.Button(frame_verify, text="Chọn ảnh chữ ký", command=self.select_signature_to_verify).pack(pady=5)
        
#         # Hiển thị ảnh đã chọn
#         self.signature_label = ttk.Label(frame_verify, text="Chưa có ảnh chữ ký được chọn")
#         self.signature_label.pack(pady=5)
        
#         # Nút xác nhận
#         ttk.Button(frame_verify, text="Xác nhận", command=self.verify_signature).pack(pady=5)
        
#         # Làm mới danh sách khách hàng active
#         self.refresh_verify_customer_list()

#     def refresh_customer_list(self):
#         # Xóa danh sách hiện tại
#         for item in self.tree.get_children():
#             self.tree.delete(item)
        
#         # Lấy danh sách khách hàng chưa kích hoạt
#         cursor.execute("SELECT MKH, HOTEN FROM KHACHHANG WHERE TT = 0")
#         inactive_customers = cursor.fetchall()
        
#         # Thêm vào treeview
#         for customer in inactive_customers:
#             self.tree.insert("", "end", values=(customer['MKH'], customer['HOTEN']))
        
#         # Cập nhật combobox
#         self.customer_dropdown['values'] = [str(customer['MKH']) for customer in inactive_customers]

#     def refresh_verify_customer_list(self):
#         # Lấy danh sách tất cả khách hàng để xác thực
#         cursor.execute("SELECT MKH FROM KHACHHANG")
#         all_customers = cursor.fetchall()
#         self.verify_customer_dropdown['values'] = [str(customer['MKH']) for customer in all_customers]

#     def on_customer_select(self, event):
#         self.selected_customer_id = self.customer_var.get()
#         self.selected_images = []
#         self.image_listbox.delete(0, tk.END)
#         messagebox.showinfo("Thông báo", f"Đã chọn khách hàng {self.selected_customer_id}. Vui lòng thêm ít nhất 3 ảnh chữ ký mẫu.")

#     def add_signature_images(self):
#         if not self.selected_customer_id:
#             messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng trước!")
#             return
        
#         # Chọn nhiều ảnh
#         files = filedialog.askopenfilenames(
#             title="Chọn ảnh chữ ký",
#             filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
#         )
        
#         for file in files:
#             self.selected_images.append(file)
#             self.image_listbox.insert(tk.END, os.path.basename(file))
        
#         if len(self.selected_images) < 3:
#             messagebox.showinfo("Thông báo", f"Đã chọn {len(self.selected_images)} ảnh. Cần ít nhất 3 ảnh chữ ký mẫu.")

#     def save_signatures(self):
#         if not self.selected_customer_id:
#             messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng trước!")
#             return
        
#         if len(self.selected_images) < 3:
#             messagebox.showwarning("Cảnh báo", f"Chưa đủ chữ ký mẫu. Cần ít nhất 3 ảnh, hiện có: {len(self.selected_images)}")
#             return
        
#         # Tạo thư mục cho khách hàng mới trong new_customer
#         customer_dir = os.path.join(new_customer_dir, self.selected_customer_id)
#         os.makedirs(customer_dir, exist_ok=True)
        
#         # Sao chép ảnh vào thư mục new_customer
#         for img_path in self.selected_images:
#             dest_path = os.path.join(customer_dir, os.path.basename(img_path))
#             shutil.copy2(img_path, dest_path)
        
#         # Trích xuất đặc trưng
#         new_features = []
#         temp_paths = []
#         new_customer_ids_list = []
#         for file in os.listdir(customer_dir):
#             if file.lower().endswith(image_extensions):
#                 image_path = os.path.join(customer_dir, file)
#                 features = extract_features(image_path, feature_extractor)
#                 new_features.append(features)
#                 temp_paths.append(image_path)
#                 new_customer_ids_list.append(self.selected_customer_id)
        
#         # Di chuyển thư mục vào Reference
#         reference_customer_path = os.path.join(reference_dir, self.selected_customer_id)
#         shutil.move(customer_dir, reference_customer_path)
        
#         # Cập nhật đường dẫn
#         new_paths = []
#         for temp_path in temp_paths:
#             file_name = os.path.basename(temp_path)
#             new_path = os.path.join(reference_customer_path, file_name)
#             new_paths.append(new_path)
        
#         # Thêm vào FAISS index
#         new_features_array = np.array(new_features, dtype=np.float32)
#         index.add(new_features_array)
        
#         # Cập nhật danh sách thông tin
#         signature_paths.extend(new_paths)
#         signature_customer_ids.extend(new_customer_ids_list)
#         customer_ids.append(self.selected_customer_id)
#         customer_to_index[self.selected_customer_id] = len(customer_ids) - 1
        
#         # Kích hoạt khách hàng trong database
#         cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (self.selected_customer_id,))
#         conn.commit()
        
#         messagebox.showinfo("Thành công", f"Đã kích hoạt khách hàng {self.selected_customer_id} với {len(new_features)} chữ ký mẫu.")
        
#         # Làm mới danh sách
#         self.refresh_customer_list()
#         self.refresh_verify_customer_list()
#         self.selected_images = []
#         self.image_listbox.delete(0, tk.END)

#     def select_signature_to_verify(self):
#         file = filedialog.askopenfilename(
#             title="Chọn ảnh chữ ký",
#             filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
#         )
#         if file:
#             # Sao chép ảnh vào thư mục Current
#             dest_path = os.path.join(current_dir, "current_signature.jpg")
#             shutil.copy2(file, dest_path)
#             self.signature_label.config(text=f"Đã chọn: {os.path.basename(file)}")
            
#             # Hiển thị ảnh
#             img = Image.open(file)
#             img = img.resize((150, 150), Image.LANCZOS)
#             photo = ImageTk.PhotoImage(img)
#             self.signature_label.config(image=photo, text="")
#             self.signature_label.image = photo

#     def verify_signature(self):
#         customer_id = self.verify_customer_var.get()
#         if not customer_id:
#             messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
#             return
        
#         current_signature_path = os.path.join(current_dir, "current_signature.jpg")
#         if not os.path.exists(current_signature_path):
#             messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh chữ ký!")
#             return
        
#         # Trích xuất đặc trưng từ chữ ký hiện tại
#         current_features = extract_features(current_signature_path, feature_extractor)
        
#         # Tìm kiếm chữ ký mẫu gần nhất bằng FAISS
#         k = 1
#         current_features = np.array([current_features], dtype=np.float32)
#         distances, indices = index.search(current_features, k)
        
#         # Lấy thông tin chữ ký mẫu gần nhất
#         best_match_index = indices[0][0]
#         best_match_distance = distances[0][0]
#         best_match_path = signature_paths[best_match_index]
#         best_match_customer = signature_customer_ids[best_match_index]
        
#         # Tính độ tương đồng
#         max_distance = 1e6
#         similarity = 1 - (best_match_distance / max_distance)
#         if similarity < 0:
#             similarity = 0
        
#         # Hiển thị kết quả
#         plt.figure(figsize=(10, 5))
#         plt.subplot(1, 2, 1)
#         plt.imshow(load_img(current_signature_path))
#         plt.title("Chữ ký hiện tại")
#         plt.axis('off')
        
#         plt.subplot(1, 2, 2)
#         plt.imshow(load_img(best_match_path))
#         plt.title(f"Chữ ký mẫu của MKH: {best_match_customer}\nSimilarity: {similarity:.4f}")
#         plt.axis('off')
#         plt.show()
        
#         # Xác thực
#         threshold = 0.7 # Ngưỡng xác thực
#         if best_match_customer == customer_id and similarity >= threshold:
#             messagebox.showinfo("Kết quả", f"Success: Chữ ký khớp với khách hàng MKH: {customer_id}\nĐộ tương đồng: {similarity:.4f}")
#             # Cập nhật trạng thái khách hàng
#             cursor.execute("UPDATE KHACHHANG SET TT = 1 WHERE MKH = %s", (customer_id,))
#             conn.commit()
#         else:
#             messagebox.showwarning("Kết quả", f"Chữ ký không khớp với khách hàng MKH: {customer_id}\nTrùng khớp với MKH: {best_match_customer}\nĐộ tương đồng: {similarity:.4f}")

# # Chạy ứng dụng
# # if __name__ == "__main__":
# #     root = tk.Tk()
# #     app = SignatureVerificationApp(root)
# #     root.mainloop()
