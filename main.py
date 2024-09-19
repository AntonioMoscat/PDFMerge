import sys
import os
from typing import List
import aspose.pdf as pdf
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QMessageBox, QListWidget, QStyledItemDelegate
)
from PyQt6.QtGui import QIcon, QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QObject


class FileDrop(QObject):
    filesDropped = pyqtSignal(list)

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget = widget
        self.widget.setAcceptDrops(True)
        self.widget.dragEnterEvent = self.dragEnterEvent
        self.widget.dragMoveEvent = self.dragMoveEvent
        self.widget.dropEvent = self.dropEvent

    def dragEnterEvent(self, event):
        self._handle_drag_event(event)

    def dragMoveEvent(self, event):
        self._handle_drag_event(event)

    def _handle_drag_event(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            event.setDropAction(Qt.DropAction.CopyAction)
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            links = [str(url.toLocalFile()) for url in event.mimeData().urls()]
            self.filesDropped.emit(links)
        else:
            event.ignore()


class CustomListWidget(QListWidget):
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            self._draw_placeholder_text()

    def _draw_placeholder_text(self):
        painter = QPainter(self.viewport())
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(128, 128, 128))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Droppa qui i file")
        painter.restore()


class CustomItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if option.rect.top() == 0:
            self._draw_separator_line(painter, option)

    def _draw_separator_line(self, painter, option):
        painter.save()
        painter.setPen(QColor(200, 200, 200))
        painter.drawLine(option.rect.topLeft(), option.rect.topRight())
        painter.restore()


class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_files: List[str] = []
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("PDF Merger")
        self.setGeometry(100, 100, 400, 300)
        self._set_app_icon()

        layout = QVBoxLayout()
        self.file_list = self._create_file_list()
        layout.addWidget(self.file_list)

        self.add_button = self._create_button("Add PDF Files", self.open_file_dialog)
        layout.addWidget(self.add_button)

        self.merge_button = self._create_button("Merge PDFs", self.merge_pdfs)
        layout.addWidget(self.merge_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _set_app_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

    def _create_file_list(self):
        file_list = CustomListWidget()
        file_drop = FileDrop(file_list)
        file_drop.filesDropped.connect(self.add_files)
        return file_list

    def _create_button(self, text: str, slot):
        button = QPushButton(text)
        button.clicked.connect(slot)
        return button

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files",
            "C:/Users/"+os.environ["USERNAME"]+"/Downloads",
            "PDF Files (*.pdf)"
        )
        self.add_files(files)

    def add_files(self, files: List[str]):
        for file in files:
            if file.lower().endswith('.pdf') and file not in self.pdf_files:
                self.pdf_files.append(file)
                self.file_list.addItem(os.path.basename(file))

    def merge_pdfs(self):
        if not self.pdf_files:
            QMessageBox.warning(self, "No Files", "No PDF files selected for merging.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "", "PDF Files (*.pdf)"
        )
        if not output_file:
            return

        try:
            pdf_file_editor = pdf.facades.PdfFileEditor()
            pdf_file_editor.concatenate(self.pdf_files, output_file)
            QMessageBox.information(
                self, "Success", f"PDFs merged successfully into {output_file}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while merging PDFs: {str(e)}"
            )


def main():
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
