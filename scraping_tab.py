# scraping_tab.py
import os
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from duckduckgo_search import DDGS

class ScrapingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_urls = []
        self.current_index = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input for class name and search keyword
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

        # Fetch images button
        self.fetch_button = QPushButton("Fetch Images")
        self.fetch_button.clicked.connect(self.fetch_images)
        layout.addWidget(self.fetch_button)

        # Image preview label
        self.image_label = QLabel("Ảnh sẽ hiển thị tại đây")
        self.image_label.setFixedSize(600, 400)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Download and Skip buttons
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
        if self.current_index >= len(self.image_urls):
            return
        url = self.image_urls[self.current_index]
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                folder = os.path.join("dataset", self.class_input.text().strip())
                if not os.path.exists(folder):
                    os.makedirs(folder)
                # Build the base filename
                base_name = f"{self.class_input.text().strip()}_{self.current_index}"
                filename = os.path.join(folder, f"{base_name}.jpg")
                # If a file with the same name exists, append a counter (e.g., _2, _3, ...)
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
        self.current_index += 1
        self.show_current_image()
