# dialogs.py
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
from PyQt5.QtCore import QRect

class EditBoxDialog(QDialog):
    def __init__(self, rect, label, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Bounding Box")
        self.rect = rect  # QRect
        self.label = label

        self.x_edit = QLineEdit(str(rect.x()))
        self.y_edit = QLineEdit(str(rect.y()))
        self.width_edit = QLineEdit(str(rect.width()))
        self.height_edit = QLineEdit(str(rect.height()))
        self.label_edit = QLineEdit(str(label))

        layout = QFormLayout(self)
        layout.addRow("X:", self.x_edit)
        layout.addRow("Y:", self.y_edit)
        layout.addRow("Width:", self.width_edit)
        layout.addRow("Height:", self.height_edit)
        layout.addRow("Label:", self.label_edit)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)

    def getValues(self):
        """Trả về một QRect mới và label mới nếu dữ liệu nhập hợp lệ, ngược lại trả về (None, None)."""
        try:
            x = int(self.x_edit.text())
            y = int(self.y_edit.text())
            w = int(self.width_edit.text())
            h = int(self.height_edit.text())
            new_label = int(self.label_edit.text())
        except Exception:
            return None, None
        return QRect(x, y, w, h), new_label
