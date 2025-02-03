# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from scraping_tab import ScrapingTab
from labeling_tab import LabelingTab
from video_scraping_tab import VideoScrapingTab

class MainWindow(QMainWindow):
    def __init__(self):
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
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
