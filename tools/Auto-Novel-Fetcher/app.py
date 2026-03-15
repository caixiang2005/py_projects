import sys
import textwrap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from Auto_Novel_Fetcher import input_novel_name


class SearchThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, novel_name):
        super().__init__()
        self.novel_name = novel_name
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        }

    def run(self):
        try:
            result = input_novel_name(self.novel_name, self.headers)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.search_result = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("小说下载工具")
        self.setFixedSize(800, 600)
        self.set_window_position()
        self.setup_styles()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 20, 40, 15)

        title_label = QLabel("小说下载(双击下载)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("请输入你需要下载的小说")
        self.input_box.setFont(QFont("Microsoft YaHei", 12))
        self.input_box.setFixedHeight(45)

        self.start_btn = QPushButton("开始")
        self.start_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.start_btn.setFixedSize(100, 45)
        self.start_btn.clicked.connect(self.on_start_clicked)

        input_layout.addWidget(self.input_box, 1)
        input_layout.addWidget(self.start_btn)

        self.loading_label = QLabel("正在加载中...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setFont(QFont("Microsoft YaHei", 12))
        self.loading_label.setVisible(False)

        self.loading_bar = QProgressBar()
        self.loading_bar.setFixedHeight(4)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont("Microsoft YaHei", 11))
        self.result_list.setFixedHeight(320)
        self.result_list.itemClicked.connect(self.on_item_clicked)

        self.info_area = QTextEdit()
        self.info_area.setReadOnly(True)
        self.info_area.setFont(QFont("Microsoft YaHei", 10))
        self.info_area.setFixedHeight(120)
        self.info_area.setPlaceholderText("双击小说进行下载")

        main_layout.addWidget(title_label)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.loading_label)
        main_layout.addWidget(self.loading_bar)
        main_layout.addWidget(self.result_list, 1)
        main_layout.addWidget(self.info_area, 1)

        footer_layout = QHBoxLayout()
        self.footer_label = QLabel("大麻哈出品工具")
        self.footer_label.setFont(QFont("Microsoft YaHei", 9))
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch(1)
        self.email_label = QLabel("作者联系邮箱：2179451926@qq.com")
        self.email_label.setFont(QFont("Microsoft YaHei", 9))
        footer_layout.addWidget(self.email_label)
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

    def on_start_clicked(self):
        novel_name = self.input_box.text().strip()
        if not novel_name:
            self.result_list.clear()
            self.result_list.addItem("请输入小说名字")
            return

        self.loading_label.setVisible(True)
        self.loading_bar.setVisible(True)
        self.result_list.clear()
        self.result_list.addItem("书本加载中...")
        self.info_area.clear()
        self.start_btn.setEnabled(False)

        self.search_thread = SearchThread(novel_name)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()

    def on_search_finished(self, result):
        self.loading_label.setVisible(False)
        self.loading_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.search_result = result
        if result:
            self.result_list.clear()
            for name, data in result.items():
                self.result_list.addItem(name)
                item = self.result_list.item(self.result_list.count() - 1)
                info = data.get('info', '')
                if info:
                    info = '\n'.join(textwrap.wrap(info, width=30))
                item.setToolTip(info if info else '无详细信息')
        else:
            self.result_list.clear()
            self.result_list.addItem("未找到相关小说")

    def on_search_error(self, error_msg):
        self.loading_label.setVisible(False)
        self.loading_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.result_list.clear()
        self.result_list.addItem(f"搜索出错: {error_msg}")

    def on_item_clicked(self, item):
        name = item.text()
        if name in self.search_result:
            data = self.search_result[name]
            info = data.get('info', '无详细信息')
            self.info_area.setText(f"{info}")

    def set_window_position(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                padding: 0 15px;
                color: #2d3436;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QLineEdit::placeholder {
                color: #a4b0be;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QListWidget {
                background-color: #fff9e6;
                border: 1px solid #f0e68c;
                border-radius: 8px;
                padding: 10px;
                color: #5d4e37;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0e68c;
            }
            QListWidget::item:selected {
                background-color: #ffe6a7;
                color: #5d4e37;
            }
            QListWidget::item:tooltip {
                background-color: #fff9e6;
                border: 1px solid #f0e68c;
                border-radius: 4px;
                padding: 8px;
                color: #5d4e37;
            }
            QTextEdit {
                background-color: #fff9e6;
                border: 1px solid #f0e68c;
                border-radius: 8px;
                padding: 10px;
                color: #5d4e37;
            }
            QProgressBar {
                border: none;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
