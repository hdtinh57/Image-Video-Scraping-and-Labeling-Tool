"""
File: scraping_tab.py
Mô tả:
    Chứa lớp ScrapingTab, widget cho phép tìm kiếm và tải hình ảnh từ Internet dựa trên từ khóa
    và tên class, sử dụng API của DuckDuckGo.
"""

import os
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from duckduckgo_search import DDGS

class ScrapingTab(QWidget):
    """
    Widget để tìm kiếm và tải hình ảnh.
    Cho phép người dùng nhập tên class và từ khóa, sau đó fetch ảnh từ internet và hiển thị ảnh mẫu.
    Người dùng có thể tải ảnh về hoặc bỏ qua ảnh hiện tại.
    """
    def __init__(self, parent=None):
        """
        Khởi tạo widget ScrapingTab.
        """
        super().__init__(parent)
        self.image_urls = []
        self.current_index = 0
        self.initUI()

    def initUI(self):
        """
        Thiết lập giao diện cho tab scraping:
          - Các ô nhập tên class và từ khóa.
          - Nút fetch ảnh.
          - Label hiển thị ảnh mẫu.
          - Các nút download và skip ảnh.
        """
        layout = QVBoxLayout()

        # Input cho tên class và từ khóa tìm kiếm
        input_layout = QHBoxLayout()
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Tên class (ví dụ: cat)")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Từ khóa tìm ảnh (ví dụ: cute cat)")
        input_layout.addWidget(QLabel("Class:"))
        input_layout.addWidget(self.class_input)
        input_layout.addWidget(QLabel("Keyword:"))
        input_layout.addWidget(self.keyword_input)
        layout.addLayout(input_layout)

        # Nút fetch ảnh
        self.fetch_button = QPushButton("Fetch Images")
        self.fetch_button.clicked.connect(self.fetch_images)
        layout.addWidget(self.fetch_button)

        # Label hiển thị ảnh mẫu
        self.image_label = QLabel("Ảnh sẽ hiển thị tại đây")
        self.image_label.setFixedSize(600, 400)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Các nút download và skip ảnh
        btn_layout = QHBoxLayout()
        self.download_button = QPushButton("Download Image")
        self.download_button.clicked.connect(self.download_image)
        self.skip_button = QPushButton("Skip Image")
        self.skip_button.clicked.connect(self.skip_image)
        btn_layout.addWidget(self.download_button)
        btn_layout.addWidget(self.skip_button)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def fetch_images(self):
        """
        Lấy danh sách URL hình ảnh dựa trên từ khóa và tên class nhập vào.
        
        Sử dụng API của DuckDuckGo để lấy kết quả, sau đó lưu URL ảnh và hiển thị ảnh đầu tiên.
        Nếu không nhập đủ thông tin hoặc có lỗi xảy ra, hiển thị thông báo cho người dùng.
        """
        self.class_name = self.class_input.text().strip()
        self.keyword = self.keyword_input.text().strip()
        if not self.class_name or not self.keyword:
            QMessageBox.warning(self, "Warning", "Vui lòng nhập đầy đủ tên class và từ khóa!")
            return
        try:
            with DDGS() as ddgs:
                results = ddgs.images(self.keyword, max_results=1000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Lỗi khi fetch ảnh: {e}")
            return
        if not results:
            QMessageBox.information(self, "Info", "Không tìm thấy ảnh nào.")
            return

        self.image_urls = [item['image'] for item in results]
        self.current_index = 0
        self.show_current_image()

    def show_current_image(self):
        """
        Hiển thị ảnh hiện tại từ danh sách URL.
        
        Nếu đã duyệt hết ảnh hoặc không thể load ảnh được, hiển thị thông báo tương ứng.
        """
        if self.current_index >= len(self.image_urls):
            QMessageBox.information(self, "Info", "Đã duyệt hết ảnh!")
            self.image_label.setText("Hết ảnh!")
            return
        url = self.image_urls[self.current_index]
        try:
            response = requests.get(url, timeout=10)
            image_data = response.content
            image = QImage()
            if not image.loadFromData(image_data):
                self.image_label.setText("Lỗi: không load được dữ liệu ảnh!")
                return
            pixmap = QPixmap.fromImage(image)
            if pixmap.isNull():
                self.image_label.setText("Lỗi: QPixmap là null!")
                return
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Lỗi load ảnh: {e}")
            self.image_label.setText("Lỗi load ảnh!")

    def download_image(self):
        """
        Tải hình ảnh hiện tại về và lưu vào thư mục dataset theo tên class.
        
        Nếu file đã tồn tại, sẽ tự động thêm số thứ tự để tránh ghi đè.
        Sau khi tải xong, chuyển sang ảnh tiếp theo.
        """
        if self.current_index >= len(self.image_urls):
            return
        url = self.image_urls[self.current_index]
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                folder = os.path.join("dataset", self.class_input.text().strip())
                if not os.path.exists(folder):
                    os.makedirs(folder)
                # Xây dựng tên file cơ bản
                base_name = f"{self.class_input.text().strip()}_{self.current_index}"
                filename = os.path.join(folder, f"{base_name}.jpg")
                # Nếu file đã tồn tại, thêm đuôi số (_2, _3, ...)
                counter = 2
                while os.path.exists(filename):
                    filename = os.path.join(folder, f"{base_name}_{counter}.jpg")
                    counter += 1
                with open(filename, "wb") as f:
                    f.write(response.content)
                QMessageBox.information(self, "Info", f"Ảnh đã lưu: {filename}")
            else:
                QMessageBox.warning(self, "Warning", "Download ảnh thất bại!")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Lỗi download ảnh: {e}")
        self.current_index += 1
        self.show_current_image()

    def skip_image(self):
        """
        Bỏ qua ảnh hiện tại và chuyển sang ảnh tiếp theo.
        """
        self.current_index += 1
        self.show_current_image()
