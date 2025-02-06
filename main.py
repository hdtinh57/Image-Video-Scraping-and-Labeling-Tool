"""
File: main.py
Mô tả:
    Đây là file chính của ứng dụng, quản lý giao diện chính với 3 tab:
      - Image Scraping: Dùng để tìm kiếm và tải hình ảnh.
      - Image Labeling: Dùng để gán nhãn (label) cho hình ảnh.
      - Video Scraping: Dùng để tải video từ file hoặc từ YouTube.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from scraping_tab import ScrapingTab
from labeling_tab import LabelingTab
from video_scraping_tab import VideoScrapingTab

class MainWindow(QMainWindow):
    """
    Lớp MainWindow tạo cửa sổ chính của ứng dụng.
    
    Chứa 3 tab chính:
      - Tab Scraping hình ảnh.
      - Tab Labeling hình ảnh.
      - Tab Scraping video.
    """
    def __init__(self):
        """
        Khởi tạo cửa sổ chính, thiết lập tiêu đề, kích thước và các tab.
        """
        super().__init__()
        self.setWindowTitle("Image & Video Scraping and Labeling Tool")
        self.resize(900, 750)
        self.tabs = QTabWidget()
        self.scraping_tab = ScrapingTab()
        self.labeling_tab = LabelingTab()
        self.video_scraping_tab = VideoScrapingTab()
        self.tabs.addTab(self.scraping_tab, "Image Scraping")
        self.tabs.addTab(self.labeling_tab, "Image Labeling")
        self.tabs.addTab(self.video_scraping_tab, "Video Scraping")
        self.setCentralWidget(self.tabs)

def main():
    """
    Hàm main khởi động ứng dụng.
    
    Tạo đối tượng QApplication, cửa sổ chính và chạy vòng lặp chính của ứng dụng.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
