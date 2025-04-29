/*Chạy bằng MySQL*/
DROP DATABASE IF EXISTS quanlykhachhang;
CREATE DATABASE quanlykhachhang;
USE quanlykhachhang;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*Tạo bảng*/
CREATE TABLE `DANHMUCCHUCNANG` (
    `MCN` VARCHAR(50) NOT NULL COMMENT 'Mã chức năng',
    `TEN` VARCHAR(255) NOT NULL COMMENT 'Tên chức năng',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    PRIMARY KEY(MCN) 
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE `CTQUYEN` (
    `MNQ` INT(11) NOT NULL COMMENT 'Mã nhóm quyền',
    `MCN` VARCHAR(50) NOT NULL COMMENT 'Mã chức năng',
    `HANHDONG` VARCHAR(255) NOT NULL COMMENT 'Hành động thực hiện',
    PRIMARY KEY(MNQ, MCN, HANHDONG)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE `NHOMQUYEN` (
    `MNQ` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã nhóm quyền',
    `TEN` VARCHAR(255) NOT NULL COMMENT 'Tên nhóm quyền',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    PRIMARY KEY(MNQ) 
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE `NHANVIEN` (
    `MNV` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã nhân viên',
    `HOTEN` VARCHAR(255) NOT NULL COMMENT 'Họ và tên NV',
    `GIOITINH` INT(11) NOT NULL COMMENT 'Giới tính',
    `NGAYSINH` DATE NOT NULL COMMENT 'Ngày sinh',
    `SDT` VARCHAR(11) NOT NULL COMMENT 'Số điện thoại',
    `EMAIL` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Email',
    `MCV` INT(11) NOT NULL COMMENT 'Mã chức vụ',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    PRIMARY KEY(MNV)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE `CHUCVU` (
    `MCV` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã chức vụ',
    `TEN` VARCHAR(255) NOT NULL COMMENT 'Họ chức vụ',
    `MUCLUONG` INT(11) NOT NULL COMMENT 'Mức lương',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    PRIMARY KEY(MCV)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE `TAIKHOAN` (
    `MNV` INT(11) NOT NULL COMMENT 'Mã nhân viên',
    `MK` VARCHAR(255) NOT NULL COMMENT 'Mật khẩu',
    `TDN` VARCHAR(255) NOT NULL UNIQUE COMMENT 'Tên đăng nhập',
    `MNQ` INT(11) NOT NULL COMMENT 'Mã nhóm quyền',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    `OTP` VARCHAR(50) DEFAULT NULL COMMENT 'Mã OTP',
    PRIMARY KEY(MNV, TDN)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE `KHACHHANG` (
    `MKH` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã khách hàng',
    `HOTEN` VARCHAR(255) NOT NULL COMMENT 'Họ và tên KH',
    `NGAYTHAMGIA` DATE NOT NULL COMMENT 'Ngày tạo dữ liệu',
    `DIACHI` VARCHAR(255) COMMENT 'Địa chỉ',
    `SDT` VARCHAR(11) UNIQUE NOT NULL COMMENT 'Số điện thoại',
    `EMAIL` VARCHAR(50) UNIQUE COMMENT 'Email',
    `CCCD` VARCHAR(11) COMMENT 'Số CCCD',
    `TIEN` INT(11) COMMENT 'Số tiền của khánh hàng',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    PRIMARY KEY(MKH)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;


CREATE TABLE `GIAODICH` (
    `MGD` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã giao dịch',
    `MKH` INT(11) NOT NULL COMMENT 'Mã khách hàng',
    `MNV` INT(11) NOT NULL COMMENT 'Mã nhân viên',
    `NGAYGIAODICH`DATETIME DEFAULT current_timestamp() COMMENT 'Ngày tạo giao dịch',
    `TIEN` INT(11) COMMENT 'Số tiền giao dịch',
    `TIENKH` INT(11) COMMENT 'Số tiền khách hàng tại thời điểm đó',
    `TT` INT(11) NOT NULL DEFAULT 1 COMMENT 'Trạng thái',
    PRIMARY KEY(MGD)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*Thêm dữ liệu*/

INSERT INTO `DANHMUCCHUCNANG`(`MCN`, `TEN`, `TT`)
VALUES 
        ('khachhang', 'Quản lý khách hàng', 1),
        ('nhanvien', 'Quản lý nhân viên', 1),
        ('chucvu', 'Quản lý chức vụ', 1),
        ('nhomquyen', 'Quản lý nhóm quyền', 1),
        ('taikhoan', 'Quản lý tài khoản', 1),
        ('giaodich', 'Quản lý giao dịch', 1);

INSERT INTO `CTQUYEN` (`MNQ`, `MCN`, `HANHDONG`)
VALUES
        (1, 'khachhang', 'create'),
        (1, 'khachhang', 'delete'),
        (1, 'khachhang', 'update'),
        (1, 'khachhang', 'view'),
        (1, 'nhanvien', 'create'),
        (1, 'nhanvien', 'delete'),
        (1, 'nhanvien', 'update'),
        (1, 'nhanvien', 'view'),
        (1, 'chucvu', 'create'),
        (1, 'chucvu', 'delete'),
        (1, 'chucvu', 'update'),
        (1, 'chucvu', 'view'),
        (1, 'nhomquyen', 'create'),
        (1, 'nhomquyen', 'delete'),
        (1, 'nhomquyen', 'update'),
        (1, 'nhomquyen', 'view'),
        (1, 'taikhoan', 'create'),
        (1, 'taikhoan', 'delete'),
        (1, 'taikhoan', 'update'),
        (1, 'taikhoan', 'view'),
        (2, 'khachhang', 'create'),
        (2, 'khachhang', 'delete'),
        (2, 'khachhang', 'update'),
        (2, 'khachhang', 'view'),
        (2, 'giaodich', 'create'),
        (2, 'giaodich', 'delete'),
        (2, 'giaodich', 'update'),
        (2, 'giaodich', 'view'),
        (3, 'khachhang', 'create'),
        (3, 'khachhang', 'delete'),
        (3, 'khachhang', 'update'),
        (3, 'khachhang', 'view');

INSERT INTO `NHOMQUYEN` (`TEN`, `TT`)
VALUES
        ('Quản lý tổng', 1),
        ('Quản lý giao dịch', 1),
        ('Nhân viên giao dịch', 1);

INSERT INTO `NHANVIEN` (`HOTEN`, `GIOITINH`, `NGAYSINH`, `SDT`, `EMAIL`, `MCV`, `TT`)
VALUES
        ('Lê Thế Minh', 0, '2077-01-01', '0505555505', 'remchan.com@gmail.com', 1, 1),
        ('Huỳnh Khôi Nguyên', 1, '2023-05-06', '0123456789', 'nguyeney111@gmail.com', 2, 1),
        ('Trần Gia Nguyễn', 1, '2004-07-17', '0387913347', 'trangianguyen.com@gmail.com', 3, 1),
        ('Hoàng Gia Bảo', 1, '2003-04-11', '0355374322', 'musicanime2501@gmail.com', 3, 1);

INSERT INTO `CHUCVU` (`TEN`, `MUCLUONG`, `TT`)
VALUES
        ('Quản lý tổng', 5000000, 1),
        ('Quản lý giao dịch', 4000000, 1),
        ('Nhân viên giao dịch', 2000000, 1);

INSERT INTO `TAIKHOAN` (`MNV`, `TDN`, `MK`, `MNQ`, `TT`, `OTP`)
VALUES
        (1, 'admin', '123456', 1, 1, 'null'),
        (2, 'NV2', '123456', 2, 1, 'null');

INSERT INTO `KHACHHANG` (`HOTEN`, `DIACHI`, `SDT`, `CCCD`, `TIEN`, `TT`, `NGAYTHAMGIA`)
VALUES
        ('Nguyễn Văn A', 'Gia Đức, Ân Đức, Hoài Ân, Bình Định', '0387913347', '082300100001', 50000000, 1, '2024-04-15 09:52:29'),
        ('Trần Nhất Nhất', '205 Trần Hưng Đạo, Phường 10, Quận 5, Thành phố Hồ Chí Minh', '0123456789', '082300020002', 40000000, 0, '2024-04-15 09:52:29'),
        ('Hoàng Gia Bo', 'Khoa Trường, Hoài Ân, Bình Định', '0987654321', '082303000003', 20000000, 0, '2024-04-15 09:52:29'),
        ('Hồ Minh Hưng', 'Khoa Trường, Hoài Ân, Bình Định', '0867987456', '082300004004', 80000000, 0, '2024-04-15 09:52:29'),
        ('Nguyễn Thị Minh Anh', '123 Phố Huế, Quận Hai Bà Trưng, Hà Nội', '0935123456', '082300050005', 8000000, 1, '2024-04-16 17:59:57'),
        ('Trần Đức Minh', '789 Đường Lê Hồng Phong, Thành phố Đà Nẵng', '0983456789', '082300060006', 4000000, 0, '2024-04-16 18:08:12'),
        ('Lê Hải Yến', '456 Tôn Thất Thuyết, Quận 4, Thành phố Hồ Chí Minh', '0977234567', '082370000007', 3000000, 0, '2024-04-16 18:08:47'),
        ('Phạm Thanh Hằng', '102 Lê Duẩn, Thành phố Hải Phòng', '0965876543', '082300000908', 2000000, 0, '2024-04-16 18:12:59'),
        ('Hoàng Đức Anh', '321 Lý Thường Kiệt, Thành phố Cần Thơ', '0946789012', '082300800009', 1000000, 0, '2024-04-16 18:13:47'),
        ('Ngô Thanh Tùng', '987 Trần Hưng Đạo, Quận 1, Thành phố Hồ Chí Minh', '0912345678', '082300000010', 10000000, 1, '2024-04-16 18:14:12'),
        ('Võ Thị Kim Ngân', '555 Nguyễn Văn Linh, Quận Nam Từ Liêm, Hà Nội', '0916789123', '082302000011', 90000000, 0, '2024-04-16 18:15:11'),
        ('Đỗ Văn Tú', '777 Hùng Vương, Thành phố Huế', '0982345678', '082300030012', 7000000, 0, '2024-04-30 18:15:56'),
        ('Lý Thanh Trúc', '888 Nguyễn Thái Học, Quận Ba Đình, Hà Nội', '0982123456', '082304000013', 4000000, 0, '2024-04-16 18:16:22'),
        ('Bùi Văn Hoàng', '222 Đường 2/4, Thành phố Nha Trang', '0933789012', '082300050014', 5000000, 0, '2024-04-16 18:16:53'),
        ('Lê Văn Thành', '23 Đường 3 Tháng 2, Quận 10, TP. Hồ Chí Minh', '0933456789', '082300600015', 100000000, 0, '2024-04-16 18:17:46'),
        ('Nguyễn Thị Lan Anh', '456 Lê Lợi, Quận 1, TP. Hà Nội', '0965123456', '082300007016', 40000000,0, '2024-04-16 18:18:10'),
        ('Phạm Thị Mai', '234 Lê Hồng Phong, Quận 5, TP. Hồ Chí Minh', '0946789013', '082300060017', 60000000, 0, '2024-04-17 18:18:34'),
        ('Hoàng Văn Nam', ' 567 Phố Huế, Quận Hai Bà Trưng, Hà Nội', '0912345679', '082300008018', 70000000, 0, '2024-04-17 18:19:16');

INSERT INTO `GIAODICH` (`MKH`, `MNV`, `TIEN`, `TT`, `TIENKH`)
VALUES
    (1, 3, 200000, 1, (SELECT TIEN FROM KHACHHANG WHERE MKH = 1) + 200000),  -- Nạp 200,000 vào tài khoản khách hàng 1, trạng thái thành công
    (2, 3, 300000, 1, (SELECT TIEN FROM KHACHHANG WHERE MKH = 2) + 300000),  -- Nạp 300,000 vào tài khoản khách hàng 2, trạng thái thành công
    (3, 3, 500000, 1, (SELECT TIEN FROM KHACHHANG WHERE MKH = 3) + 500000),  -- Nạp 500,000 vào tài khoản khách hàng 3, trạng thái thành công
    (4, 3, -100000, 1, (SELECT TIEN FROM KHACHHANG WHERE MKH = 4) - 100000),  -- Rút 100,000 từ tài khoản khách hàng 4, trạng thái thành công
    (5, 3, -500000, 0, (SELECT TIEN FROM KHACHHANG WHERE MKH = 5) - 500000),  -- Rút 500,000 từ tài khoản khách hàng 5, trạng thái hủy
    (6, 3, -700000, 2, (SELECT TIEN FROM KHACHHANG WHERE MKH = 6) - 700000);  -- Rút 700,000 từ tài khoản khách hàng 6, trạng thái đang xử lý

        
/*Tạo quan hệ*/

ALTER TABLE `CTQUYEN` ADD CONSTRAINT FK_MNQ_CTQUYEN FOREIGN KEY (MNQ) REFERENCES `NHOMQUYEN`(MNQ) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `CTQUYEN` ADD CONSTRAINT FK_MCN_CTQUYEN FOREIGN KEY (MCN) REFERENCES `DANHMUCCHUCNANG`(MCN) ON DELETE NO ACTION ON UPDATE NO ACTION;           

ALTER TABLE `TAIKHOAN` ADD CONSTRAINT FK_MNV_TAIKHOAN FOREIGN KEY (MNV) REFERENCES `NHANVIEN`(MNV) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `TAIKHOAN` ADD CONSTRAINT FK_MNQ_TAIKHOAN FOREIGN KEY (MNQ) REFERENCES `NHOMQUYEN`(MNQ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `NHANVIEN` ADD CONSTRAINT FK_MCV_NHANVIEN FOREIGN KEY (MCV) REFERENCES `CHUCVU`(MCV) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `GIAODICH` ADD CONSTRAINT FK_MNV_GIAODICH FOREIGN KEY (MNV) REFERENCES `NHANVIEN`(MNV) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `GIAODICH` ADD CONSTRAINT FK_MKH_GIAODICH FOREIGN KEY (MKH) REFERENCES `KHACHHANG`(MKH) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;