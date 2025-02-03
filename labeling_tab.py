# labeling_tab.py
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QMessageBox, QInputDialog, QDialog)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from dialogs import EditBoxDialog

class ImageLabelerWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.image = None          # Ảnh gốc (QImage)
        self.scaled_image = None   # Ảnh đã scale để hiển thị
        self.boxes = []            # Danh sách các bounding box: list of tuples (QRect, label)
        self.drawing = False
        self.start_point = QPoint()
        self.current_rect = QRect()
        self.scale_factor = 1.0
        # Đặt stylesheet và đảm bảo không có margins
        self.setStyleSheet("background-color: #eee;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # Stack cho undo/redo
        self.undo_stack = []
        self.redo_stack = []

    def push_undo_state(self):
        state = [(QRect(r.x(), r.y(), r.width(), r.height()), label) for (r, label) in self.boxes]
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def do_undo(self):
        if self.undo_stack:
            current_state = [(QRect(r.x(), r.y(), r.width(), r.height()), label) for (r, label) in self.boxes]
            self.redo_stack.append(current_state)
            self.boxes = self.undo_stack.pop()
            self.update()

    def do_redo(self):
        if self.redo_stack:
            current_state = [(QRect(r.x(), r.y(), r.width(), r.height()), label) for (r, label) in self.boxes]
            self.undo_stack.append(current_state)
            self.boxes = self.redo_stack.pop()
            self.update()

    def setImage(self, image_path):
        self.image_file = image_path
        self.image = QImage(image_path)
        if self.image.isNull():
            return
        # Đảm bảo widget không có margins và căn lề lên trên – trái
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # Tính scale factor dựa trên kích thước widget hiện tại và ảnh gốc
        self.scale_factor = min(self.width() / self.image.width(), self.height() / self.image.height())
        new_width = int(self.image.width() * self.scale_factor)
        new_height = int(self.image.height() * self.scale_factor)
        self.scaled_image = self.image.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.scaled_image))
        self.boxes = []
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None:
            self.drawing = True
            self.start_point = event.pos()
            self.current_rect = QRect(self.start_point, QSize())
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.current_rect = QRect(self.start_point, event.pos()).normalized()
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            self.current_rect = QRect(self.start_point, event.pos()).normalized()
            if self.current_rect.width() > 10 and self.current_rect.height() > 10:
                self.push_undo_state()
                label, ok = QInputDialog.getInt(self, "Input Label", "Nhập id label (số nguyên):")
                if ok:
                    self.boxes.append((self.current_rect, label))
            self.current_rect = QRect()
            self.update()
        else:
            super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        pos = event.pos()
        selected_index = None
        for i, (rect, label) in enumerate(self.boxes):
            if rect.contains(pos):
                selected_index = i
                break
        if selected_index is None:
            return super().contextMenuEvent(event)
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        edit_action = menu.addAction("Edit Bounding Box")
        delete_action = menu.addAction("Delete Bounding Box")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == edit_action:
            self.push_undo_state()
            rect, label = self.boxes[selected_index]
            dialog = EditBoxDialog(rect, label, self)
            if dialog.exec_() == QDialog.Accepted:
                new_rect, new_label = dialog.getValues()
                if new_rect is not None:
                    self.boxes[selected_index] = (new_rect, new_label)
                    self.update()
        elif action == delete_action:
            self.push_undo_state()
            del self.boxes[selected_index]
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.image is None or self.scaled_image is None:
            return
        painter = QPainter(self)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        for rect, label in self.boxes:
            painter.drawRect(rect)
            painter.drawText(rect.topLeft() + QPoint(2, -2), str(label))
        if self.drawing:
            painter.drawRect(self.current_rect)

    def loadBoxesFromFile(self, label_file):
        if self.image is None:
            return
        self.boxes = []
        if not os.path.exists(label_file):
            return
        img_width = self.image.width()
        img_height = self.image.height()
        try:
            with open(label_file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        cls, cx, cy, w, h = parts
                        try:
                            cls = int(cls)
                            # Tính tọa độ gốc dựa trên ảnh gốc
                            cx = float(cx) * img_width
                            cy = float(cy) * img_height
                            w = float(w) * img_width
                            h = float(h) * img_height
                            x1 = int(cx - w / 2)
                            y1 = int(cy - h / 2)
                            # Lưu BB theo tọa độ ảnh gốc
                            rect = QRect(x1, y1, int(w), int(h))
                            # Sau đó chuyển đổi sang tọa độ của ảnh đã scale bằng cách nhân scale_factor
                            scaled_rect = QRect(
                                int(rect.x() * self.scale_factor),
                                int(rect.y() * self.scale_factor),
                                int(rect.width() * self.scale_factor),
                                int(rect.height() * self.scale_factor)
                            )
                            self.boxes.append((scaled_rect, cls))
                        except Exception as e:
                            print("Lỗi parse label:", e)
            self.update()
        except Exception as e:
            print("Lỗi load file label:", e)

    def clearBoxes(self):
        self.boxes = []
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update()


class LabelingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_files = []
        self.current_index = -1
        self.current_folder = ""
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        self.folder_combo = QComboBox()
        self.folder_combo.currentIndexChanged.connect(lambda: self.load_images())
        self.refresh_button = QPushButton("Refresh Folders")
        self.refresh_button.clicked.connect(self.load_folders)
        folder_layout.addWidget(QLabel("Chọn folder (class):"))
        folder_layout.addWidget(self.folder_combo)
        folder_layout.addWidget(self.refresh_button)
        layout.addLayout(folder_layout)

        self.image_name_label = QLabel("Chưa có ảnh được load")
        layout.addWidget(self.image_name_label)

        self.image_labeler = ImageLabelerWidget()
        self.image_labeler.setFixedSize(600, 400)
        layout.addWidget(self.image_labeler)

        btn_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Image")
        self.prev_button.clicked.connect(self.load_prev_image)
        self.next_button = QPushButton("Next Image")
        self.next_button.clicked.connect(self.load_next_image)
        self.save_button = QPushButton("Save Label")
        self.save_button.clicked.connect(self.save_label)
        self.clear_button = QPushButton("Clear Annotations")
        self.clear_button.clicked.connect(self.clear_annotations)
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)
        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo)
        self.delete_image_button = QPushButton("Delete Image")
        self.delete_image_button.clicked.connect(self.delete_current_image)
        btn_layout.addWidget(self.prev_button)
        btn_layout.addWidget(self.next_button)
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.clear_button)
        btn_layout.addWidget(self.undo_button)
        btn_layout.addWidget(self.redo_button)
        btn_layout.addWidget(self.delete_image_button)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_folders()

    def load_folders(self):
        self.folder_combo.clear()
        base_dir = "dataset"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
        self.folder_combo.addItems(folders)
        if folders:
            self.folder_combo.setCurrentIndex(0)
            self.current_folder = os.path.join(base_dir, folders[0])
            self.load_images()

    def load_images(self):
        folder = os.path.join("dataset", self.folder_combo.currentText())
        self.current_folder = folder
        self.image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        self.image_files.sort()
        if self.image_files:
            self.current_index = 0
            self.load_current_image()
        else:
            self.current_index = -1
            self.image_name_label.setText("Không có ảnh trong folder này.")
            self.image_labeler.clearBoxes()
            self.image_labeler.clear()

    def load_current_image(self):
        if self.current_index < 0 or self.current_index >= len(self.image_files):
            return
        image_path = os.path.join(self.current_folder, self.image_files[self.current_index])
        self.image_name_label.setText(f"Ảnh: {self.image_files[self.current_index]}")
        self.image_labeler.setImage(image_path)
        label_file = os.path.splitext(image_path)[0] + ".txt"
        self.image_labeler.loadBoxesFromFile(label_file)

    def load_next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()

    def load_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()

    def save_label(self):
        if self.current_index < 0 or self.current_index >= len(self.image_files):
            return
        image_path = os.path.join(self.current_folder, self.image_files[self.current_index])
        label_file = os.path.splitext(image_path)[0] + ".txt"
        if self.image_labeler.image is None:
            return
        img_width = self.image_labeler.image.width()
        img_height = self.image_labeler.image.height()
        scale = self.image_labeler.scale_factor
        try:
            with open(label_file, "w") as f:
                for rect, label in self.image_labeler.boxes:
                    orig_x = rect.x() / scale
                    orig_y = rect.y() / scale
                    orig_w = rect.width() / scale
                    orig_h = rect.height() / scale
                    x_center = (orig_x + orig_w / 2) / img_width
                    y_center = (orig_y + orig_h / 2) / img_height
                    w_norm = orig_w / img_width
                    h_norm = orig_h / img_height
                    f.write(f"{label} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
            QMessageBox.information(self, "Info", "Label đã được lưu.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Lỗi khi lưu label: {e}")

    def clear_annotations(self):
        self.image_labeler.clearBoxes()

    def undo(self):
        self.image_labeler.do_undo()

    def redo(self):
        self.image_labeler.do_redo()

    def delete_current_image(self):
        if self.current_index < 0 or self.current_index >= len(self.image_files):
            return
        image_path = os.path.join(self.current_folder, self.image_files[self.current_index])
        reply = QMessageBox.question(self, "Delete Image",
                                     f"Bạn có chắc chắn xóa ảnh {self.image_files[self.current_index]} không?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(image_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Lỗi khi xóa ảnh: {e}")
                return
            label_file = os.path.splitext(image_path)[0] + ".txt"
            if os.path.exists(label_file):
                try:
                    os.remove(label_file)
                except Exception as e:
                    print("Lỗi xóa file label:", e)
            QMessageBox.information(self, "Info", "Ảnh đã được xóa.")
            del self.image_files[self.current_index]
            if not self.image_files:
                self.current_index = -1
                self.image_labeler.clear()
                self.image_name_label.setText("Không còn ảnh nào.")
            else:
                if self.current_index >= len(self.image_files):
                    self.current_index = len(self.image_files) - 1
                self.load_current_image()
