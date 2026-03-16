import sys
import textwrap
import os
import requests as req
from lxml import etree
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from Auto_Novel_Fetcher import input_novel_name, in_book, get_book_with_callback


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


class GetBookInfoThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        }

    def run(self):
        try:
            result = in_book(self.url, self.headers)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    progress = pyqtSignal(str)
    progress_percent = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, book_name, total_chapters):
        super().__init__()
        self.url = url
        self.book_name = book_name
        self.total_chapters = total_chapters
        self.current_chapter = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        }

    def run(self):
        try:
            def progress_callback(msg):
                if '写入完成' in msg and self.total_chapters > 0:
                    self.current_chapter += 1
                    percent = int((self.current_chapter / self.total_chapters) * 100)
                    self.progress_percent.emit(percent)
                self.progress.emit(msg)

            get_book_with_callback(self.url, self.book_name, self.headers, progress_callback)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class DownloadWindow(QWidget):
    def __init__(self, book_name, book_url, book_info):
        super().__init__()
        self.book_name = book_name
        self.book_url = book_url
        self.book_info = book_info
        self.download_url = None
        self.total_chapters = 0
        self.init_ui()
        self.get_book_info()

    def init_ui(self):
        self.setWindowTitle(f"下载 - {self.book_name}")
        self.setFixedSize(600, 500)
        self.set_window_position()
        self.setup_styles()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 20, 30, 20)

        self.title_label = QLabel(self.book_name)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))

        self.info_label = QLabel(self.book_info if self.book_info else "暂无简介")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Microsoft YaHei", 10))
        self.info_label.setFixedHeight(80)

        self.chapter_label = QLabel("总章节数：加载中...")
        self.chapter_label.setFont(QFont("Microsoft YaHei", 11))

        self.download_btn = QPushButton("开始下载")
        self.download_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.download_btn.setFixedHeight(40)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.on_download_clicked)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Microsoft YaHei", 9))

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.chapter_label)
        main_layout.addWidget(self.download_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.log_area)

        self.setLayout(main_layout)

    def get_book_info(self):
        self.log_area.setText("获取书籍信息中...")
        self.info_thread = GetBookInfoThread(self.book_url)
        self.info_thread.finished.connect(self.on_book_info_finished)
        self.info_thread.error.connect(self.on_book_info_error)
        self.info_thread.start()

    def on_book_info_finished(self, result):
        self.download_url = result[0]
        self.total_chapters = result[1]
        self.chapter_label.setText(f"总章节数：{self.total_chapters}")
        self.log_area.setText("准备就绪，点击开始下载")
        self.download_btn.setEnabled(True)

    def on_book_info_error(self, error_msg):
        self.log_area.setText(f"获取信息失败: {error_msg}")

    def on_download_clicked(self):
        self.download_btn.setEnabled(False)
        self.log_area.clear()
        self.log_area.append("正在下载，请勿终止程序...\n")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.download_thread = DownloadThread(self.download_url, self.book_name, self.total_chapters)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.progress_percent.connect(self.on_progress_percent)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def on_progress_percent(self, percent):
        self.progress_bar.setValue(percent)

    def on_download_progress(self, msg):
        self.log_area.append(msg)

    def on_download_finished(self):
        self.download_btn.setEnabled(True)
        self.log_area.append("下载完成！")

    def on_download_error(self, error_msg):
        self.download_btn.setEnabled(True)
        self.log_area.append(f"下载出错: {error_msg}")

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
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #dfe6e9;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: #fff9e6;
                border: 1px solid #f0e68c;
                border-radius: 8px;
                padding: 10px;
                color: #5d4e37;
            }
        """)


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

        title_label = QLabel("小说下载")
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
        self.result_list.setFixedHeight(280)
        self.result_list.itemClicked.connect(self.on_item_clicked)
        self.result_list.itemDoubleClicked.connect(self.on_item_double_clicked)

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
            book_info = data.get('info', '')
            self.info_area.setText(book_info if book_info else "暂无简介")

    def on_item_double_clicked(self, item):
        name = item.text()
        if name in self.search_result:
            data = self.search_result[name]
            book_url = data.get('url', '')
            book_info = data.get('info', '')
            self.info_area.setText(f"{book_info}")
            self.download_window = DownloadWindow(name, book_url, book_info)
            self.download_window.show()

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
