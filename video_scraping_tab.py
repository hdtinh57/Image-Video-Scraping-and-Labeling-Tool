"""
File: video_scraping_tab.py
Mô tả:
    Chứa widget VideoScrapingTab dùng để tải video từ file hoặc từ link YouTube,
    hiển thị frame, điều chỉnh thời gian và lưu các frame đã chọn.
"""

import os
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSlider, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from yt_dlp import YoutubeDL
from utils import format_time, parse_time, sanitize_filename

class VideoScrapingTab(QWidget):
    """
    Widget cho phép tải và xử lý video.
    
    Cho phép:
      - Nhập link YouTube hoặc chọn file video.
      - Hiển thị frame hiện tại và điều chỉnh qua slider.
      - Nhảy đến thời gian xác định và lưu frame dưới dạng ảnh.
    """
    def __init__(self, parent=None):
        """
        Khởi tạo widget VideoScrapingTab.
        """
        super().__init__(parent)
        self.cap = None
        self.current_frame_index = 0
        self.total_frames = 0
        self.current_frame = None
        self.fps = 0  # FPS của video
        self.initUI()

    def initUI(self):
        """
        Thiết lập giao diện của tab Video Scraping:
          - Ô nhập link/file video, nút browse và load video.
          - Label hiển thị frame.
          - Slider điều chỉnh frame và hiển thị thời gian.
          - Nút điều hướng (Previous/Next) và lưu frame.
        """
        layout = QVBoxLayout()

        # Input cho video file hoặc link YouTube
        input_layout = QHBoxLayout()
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Nhập link YouTube hoặc đường dẫn file video")
        input_layout.addWidget(self.video_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        input_layout.addWidget(self.browse_button)
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        input_layout.addWidget(self.load_button)
        layout.addLayout(input_layout)

        # Label hiển thị frame
        self.frame_label = QLabel("Frame sẽ hiển thị ở đây")
        self.frame_label.setFixedSize(600, 400)
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.frame_label)

        # Thanh trượt để điều chỉnh frame
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
        self.frame_slider.setTickPosition(QSlider.TicksBelow)
        self.frame_slider.setTickInterval(10)
        self.frame_slider.valueChanged.connect(self.slider_moved)
        layout.addWidget(self.frame_slider)
        
        # Nhãn hiển thị thời gian
        self.time_label = QLabel("Time: 00:00 / 00:00")
        layout.addWidget(self.time_label)
        
        # Widget nhập thời gian để nhảy đến frame tương ứng
        time_input_layout = QHBoxLayout()
        time_input_layout.addWidget(QLabel("Jump to time:"))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("ss, mm:ss, hoặc hh:mm:ss")
        time_input_layout.addWidget(self.time_input)
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.go_to_time)
        time_input_layout.addWidget(self.go_button)
        layout.addLayout(time_input_layout)

        # Các nút điều hướng và lưu frame
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Frame")
        self.prev_button.clicked.connect(self.prev_frame)
        nav_layout.addWidget(self.prev_button)
        self.next_button = QPushButton("Next Frame")
        self.next_button.clicked.connect(self.next_frame)
        nav_layout.addWidget(self.next_button)
        self.save_button = QPushButton("Save Frame")
        self.save_button.clicked.connect(self.save_frame)
        nav_layout.addWidget(self.save_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def slider_moved(self, value):
        """
        Xử lý sự kiện khi thanh trượt (slider) di chuyển.
        
        Cập nhật frame hiện tại và thời gian hiển thị.
        
        :param value: Vị trí frame tương ứng với giá trị slider.
        """
        self.current_frame_index = value
        self.show_frame(value)
        self.update_time_label()

    def update_time_label(self):
        """
        Cập nhật nhãn thời gian hiển thị dựa trên frame hiện tại và tổng số frame.
        """
        if self.fps > 0 and self.total_frames > 0:
            current_time = self.current_frame_index / self.fps
            total_time = self.total_frames / self.fps
            self.time_label.setText(f"Time: {format_time(current_time)} / {format_time(total_time)}")
        else:
            self.time_label.setText("Time: 00:00 / 00:00")

    def go_to_time(self):
        """
        Nhảy đến frame tương ứng với thời gian nhập vào.
        
        Chuyển chuỗi thời gian (ss, mm:ss, hoặc hh:mm:ss) thành số giây và tính frame index.
        Nếu định dạng không hợp lệ, hiển thị cảnh báo.
        """
        time_str = self.time_input.text().strip()
        try:
            seconds = parse_time(time_str)
        except Exception:
            QMessageBox.warning(self, "Error", "Định dạng thời gian không hợp lệ!")
            return
        if self.fps <= 0:
            QMessageBox.warning(self, "Error", "Không xác định được FPS của video.")
            return
        frame_index = int(seconds * self.fps)
        if frame_index < 0:
            frame_index = 0
        elif frame_index >= self.total_frames:
            frame_index = self.total_frames - 1
        self.current_frame_index = frame_index
        self.frame_slider.setValue(frame_index)
        self.show_frame(frame_index)
        self.update_time_label()

    def browse_file(self):
        """
        Mở hộp thoại chọn file để người dùng chọn file video từ máy tính.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Chọn file video", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.webm)")
        if filename:
            self.video_input.setText(filename)
    
    def load_video(self):
        """
        Tải video từ nguồn nhập vào (link YouTube hoặc file video).
        
        Nếu là link YouTube, sử dụng yt_dlp để tải về file video.
        Sau khi tải thành công, thiết lập các thông số (fps, tổng frame, slider, ...).
        Nếu không mở được video, hiển thị thông báo lỗi.
        """
        source = self.video_input.text().strip()
        if source.startswith("http"):
            try:
                # Sử dụng yt_dlp để tải video về với tên file là tiêu đề của video
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio/best',
                    'outtmpl': '%(title)s.%(ext)s',
                    'quiet': True,
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(source, download=True)
                    filename = ydl.prepare_filename(info_dict)
                if not os.path.exists(filename):
                    raise Exception("Không tải được file video.")
                self.video_title = info_dict.get("title", "video")
                self.cap = cv2.VideoCapture(filename)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Lỗi khi tải video YouTube bằng yt_dlp: {e}")
                return
        else:
            if not os.path.exists(source):
                QMessageBox.warning(self, "Error", "File không tồn tại!")
                return
            self.video_title = os.path.splitext(os.path.basename(source))[0]
            self.cap = cv2.VideoCapture(source)
        if self.cap is not None and self.cap.isOpened():
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.current_frame_index = 0
            self.frame_slider.setMaximum(self.total_frames - 1)
            self.frame_slider.setValue(0)
            self.show_frame(self.current_frame_index)
            self.update_time_label()
        else:
            QMessageBox.warning(self, "Error", "Không mở được video!")

    def show_frame(self, frame_index):
        """
        Hiển thị frame tương ứng với chỉ số frame_index từ video.
        
        Đọc frame từ video, chuyển đổi màu và hiển thị trên label.
        Nếu không đọc được frame, hiển thị thông báo lỗi.
        
        :param frame_index: Chỉ số frame cần hiển thị.
        """
        if self.cap is None or not self.cap.isOpened():
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.cap.read()
        if not ret:
            QMessageBox.warning(self, "Error", "Không đọc được frame!")
            return
        self.current_frame = frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = frame_rgb.shape
        bytes_per_line = channels * width
        qimg = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(self.frame_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.frame_label.setPixmap(scaled_pixmap)

    def next_frame(self):
        """
        Chuyển sang frame tiếp theo nếu chưa đạt đến frame cuối.
        """
        if self.cap is None:
            return
        if self.current_frame_index < self.total_frames - 1:
            self.current_frame_index += 1
            self.frame_slider.setValue(self.current_frame_index)
            self.show_frame(self.current_frame_index)
            self.update_time_label()

    def prev_frame(self):
        """
        Chuyển sang frame trước nếu chưa đạt đến frame đầu.
        """
        if self.cap is None:
            return
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.frame_slider.setValue(self.current_frame_index)
            self.show_frame(self.current_frame_index)
            self.update_time_label()
    
    def save_frame(self):
        """
        Lưu frame hiện tại dưới dạng file ảnh (.jpg).
        
        Tên file được xây dựng dựa trên tên video (đã được sanitize) và số thứ tự frame.
        Frame được lưu vào thư mục 'dataset/<tên_video>/'.
        """
        if self.current_frame is None:
            return
        # Lấy tên video từ thuộc tính video_title, nếu không có thì lấy từ video_input
        base = "video"
        if hasattr(self, "video_title"):
            base = self.video_title
        else:
            source = self.video_input.text().strip()
            if not source.startswith("http"):
                base = os.path.splitext(os.path.basename(source))[0]
        # Chuẩn hóa tên file
        base = sanitize_filename(base)
        # Rút gọn tên video (ví dụ: chỉ lấy 10 ký tự đầu)
        short_base = base if len(base) <= 10 else base[:10]
        save_dir = os.path.join("dataset", base)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        filename = os.path.join(save_dir, f"{short_base}_{self.current_frame_index}.jpg")
        print("Lưu frame vào:", filename)
        success = cv2.imwrite(filename, self.current_frame)
        if success:
            QMessageBox.information(self, "Saved", f"Frame đã được lưu: {filename}")
        else:
            QMessageBox.warning(self, "Error", "Không lưu được frame!")
