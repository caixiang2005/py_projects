import sys
import requests as req

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QStackedWidget,
    QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QBrush

from app import ip_search, weather_search, phone, idCard

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': "1",
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document'
}

class Worker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多功能查询工具")
        self.setMinimumSize(900, 650)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = self.create_left_panel()
        self.right_stack = QStackedWidget()

        self.ip_widget = self.create_ip_widget()
        self.weather_widget = self.create_weather_widget()
        self.phone_widget = self.create_phone_widget()
        self.idcard_widget = self.create_idcard_widget()

        self.right_stack.addWidget(self.ip_widget)
        self.right_stack.addWidget(self.weather_widget)
        self.right_stack.addWidget(self.phone_widget)
        self.right_stack.addWidget(self.idcard_widget)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.right_stack, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #eaeaea;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #16213e;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                color: #eaeaea;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0f3460;
            }
            QPushButton:checked {
                background-color: #0f3460;
                border-left: 3px solid #00d9ff;
            }
            QLineEdit {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 10px 15px;
                color: #eaeaea;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00d9ff;
            }
            QTextEdit {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 8px;
                padding: 15px;
                color: #eaeaea;
                font-size: 13px;
            }
            QLabel {
                color: #eaeaea;
            }
            QPushButton.action_btn {
                background-color: #0f3460;
                border-radius: 8px;
                padding: 12px 25px;
                text-align: center;
                font-weight: bold;
            }
            QPushButton.action_btn:hover {
                background-color: #00d9ff;
                color: #1a1a2e;
            }
            QFrame#card {
                background-color: #16213e;
                border-radius: 12px;
                padding: 20px;
            }
            QScrollArea {
                border: none;
            }
        """)
        self.setLayout(main_layout)

    def create_left_panel(self):
        frame = QFrame()
        frame.setFixedWidth(220)
        frame.setStyleSheet("""
            background-color: #16213e;
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 30, 15, 30)
        layout.setSpacing(10)

        title = QLabel("🔍 查询工具")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00d9ff;
            padding: 10px 0;
        """)
        layout.addWidget(title)

        layout.addSpacing(20)

        self.btn_ip = self.create_nav_button("🌐 IP地址查询", "ip")
        self.btn_weather = self.create_nav_button("☁️ 天气查询", "weather")
        self.btn_phone = self.create_nav_button("📱 电话归属", "phone")
        self.btn_idcard = self.create_nav_button("🪪 身份证查询", "idcard")

        layout.addWidget(self.btn_ip)
        layout.addWidget(self.btn_weather)
        layout.addWidget(self.btn_phone)
        layout.addWidget(self.btn_idcard)

        layout.addStretch()

        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(3)

        footer_top = QLabel("大马哈出品工具")
        footer_top.setStyleSheet("color: #00d9ff; font-size: 12px; font-weight: bold;")
        footer_top.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer_bottom = QLabel("2179451926@qq.com")
        footer_bottom.setStyleSheet("color: #666; font-size: 10px;")
        footer_bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer_layout.addWidget(footer_top)
        footer_layout.addWidget(footer_bottom)

        layout.addLayout(footer_layout)

        frame.setLayout(layout)
        return frame

    def create_nav_button(self, text, page):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(page))
        if page == "ip":
            btn.setChecked(True)
        return btn

    def switch_page(self, page):
        page_map = {"ip": 0, "weather": 1, "phone": 2, "idcard": 3}
        self.right_stack.setCurrentIndex(page_map[page])

        for btn in [self.btn_ip, self.btn_weather, self.btn_phone, self.btn_idcard]:
            btn.setChecked(False)

        if page == "ip":
            self.btn_ip.setChecked(True)
        elif page == "weather":
            self.btn_weather.setChecked(True)
        elif page == "phone":
            self.btn_phone.setChecked(True)
        elif page == "idcard":
            self.btn_idcard.setChecked(True)

    def create_result_text(self):
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #0d1b2a;
                border: 1px solid #1b263b;
                border-radius: 8px;
                padding: 15px;
                color: #80ed99;
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        return text_edit

    def create_card(self, title, icon, content_layout):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout()

        header = QLabel(f"{icon} {title}")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d9ff; padding: 5px 0;")
        layout.addWidget(header)

        layout.addLayout(content_layout)
        card.setLayout(layout)
        return card

    def create_ip_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("🌐 IP地址查询")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d9ff;")
        layout.addWidget(title)

        desc = QLabel("输入IP地址，查询其所在地理位置")
        desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(desc)

        layout.addSpacing(10)

        input_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("请输入IP地址，例如：123.9.8.7")
        input_layout.addWidget(self.ip_input)

        self.ip_btn = QPushButton("查询")
        self.ip_btn.setFixedWidth(100)
        self.ip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ip_btn.clicked.connect(self.do_ip_search)
        input_layout.addWidget(self.ip_btn)
        layout.addLayout(input_layout)

        self.ip_result = self.create_result_text()
        layout.addWidget(self.ip_result)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def do_ip_search(self):
        ip = self.ip_input.text().strip()
        if not ip:
            self.ip_result.setHtml("<span style='color: #ff6b6b;'>请输入有效的IP地址</span>")
            return

        self.ip_btn.setEnabled(False)
        self.ip_btn.setText("查询中...")
        self.ip_result.setHtml("<span style='color: #ffd93d;'>正在查询，请稍候...</span>")

        self.ip_worker = Worker(ip_search, ip)
        self.ip_worker.finished.connect(self.ip_search_finished)
        self.ip_worker.error.connect(self.ip_search_error)
        self.ip_worker.start()

    def ip_search_finished(self, result):
        self.ip_btn.setEnabled(True)
        self.ip_btn.setText("查询")
        if isinstance(result, str):
            self.ip_result.setHtml(f"<span style='color: #80ed99;'>{result}</span>")
        else:
            self.ip_result.setHtml(f"<span style='color: #ff6b6b;'>查询失败：{result}</span>")

    def ip_search_error(self, error):
        self.ip_btn.setEnabled(True)
        self.ip_btn.setText("查询")
        self.ip_result.setHtml(f"<span style='color: #ff6b6b;'>错误：{error}</span>")

    def create_weather_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("☁️ 天气查询")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d9ff;")
        layout.addWidget(title)

        desc = QLabel("输入城市名称，查询天气预报信息")
        desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(desc)

        layout.addSpacing(10)

        input_layout = QHBoxLayout()
        self.weather_input = QLineEdit()
        self.weather_input.setPlaceholderText("请输入城市名称，例如：柴桑区")
        input_layout.addWidget(self.weather_input)

        self.weather_btn = QPushButton("查询")
        self.weather_btn.setFixedWidth(100)
        self.weather_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.weather_btn.clicked.connect(self.do_weather_search)
        input_layout.addWidget(self.weather_btn)
        layout.addLayout(input_layout)

        self.weather_result = self.create_result_text()
        layout.addWidget(self.weather_result)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def do_weather_search(self):
        loc = self.weather_input.text().strip()
        if not loc:
            self.weather_result.setHtml("<span style='color: #ff6b6b;'>请输入有效的城市名称</span>")
            return

        self.weather_btn.setEnabled(False)
        self.weather_btn.setText("查询中...")
        self.weather_result.setHtml("<span style='color: #ffd93d;'>正在查询，请稍候...</span>")

        self.weather_worker = Worker(weather_search, loc)
        self.weather_worker.finished.connect(self.weather_search_finished)
        self.weather_worker.error.connect(self.weather_search_error)
        self.weather_worker.start()

    def weather_search_finished(self, result):
        self.weather_btn.setEnabled(True)
        self.weather_btn.setText("查询")
        if isinstance(result, dict):
            output = f"""
<div style='line-height: 1.8;'>
<p style='color: #00d9ff; font-size: 16px;'>📍 地点：{result.get('location', '未知')}</p>
<p style='color: #eaeaea;'>📅 日期：{result.get('week', '未知')}</p>
<p style='color: #80ed99;'>🌤️ 天气：{result.get('weather', '未知')}</p>
<p style='color: #ffd93d;'>🌡️ 温度：{result.get('temperature', '未知')}</p>
<p style='color: #a8dadc;'>💨 风速：{result.get('wind_speed', '未知')}</p>
</div>
            """
            self.weather_result.setHtml(output)
        else:
            self.weather_result.setHtml(f"<span style='color: #ff6b6b;'>{result}</span>")

    def weather_search_error(self, error):
        self.weather_btn.setEnabled(True)
        self.weather_btn.setText("查询")
        self.weather_result.setHtml(f"<span style='color: #ff6b6b;'>错误：{error}</span>")

    def create_phone_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("📱 电话归属查询")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d9ff;")
        layout.addWidget(title)

        desc = QLabel("输入手机号码，查询号码归属地和运营商")
        desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(desc)

        layout.addSpacing(10)

        input_layout = QHBoxLayout()
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入手机号码，例如：15180696892")
        input_layout.addWidget(self.phone_input)

        self.phone_btn = QPushButton("查询")
        self.phone_btn.setFixedWidth(100)
        self.phone_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.phone_btn.clicked.connect(self.do_phone_search)
        input_layout.addWidget(self.phone_btn)
        layout.addLayout(input_layout)

        self.phone_result = self.create_result_text()
        layout.addWidget(self.phone_result)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def do_phone_search(self):
        p = self.phone_input.text().strip()
        if not p:
            self.phone_result.setHtml("<span style='color: #ff6b6b;'>请输入有效的手机号码</span>")
            return

        self.phone_btn.setEnabled(False)
        self.phone_btn.setText("查询中...")
        self.phone_result.setHtml("<span style='color: #ffd93d;'>正在查询，请稍候...</span>")

        self.phone_worker = Worker(phone, p)
        self.phone_worker.finished.connect(self.phone_search_finished)
        self.phone_worker.error.connect(self.phone_search_error)
        self.phone_worker.start()

    def phone_search_finished(self, result):
        self.phone_btn.setEnabled(True)
        self.phone_btn.setText("查询")
        if isinstance(result, dict):
            output = f"""
<div style='line-height: 1.8;'>
<p style='color: #00d9ff; font-size: 16px;'>📍 归属地：{result.get('location', '未知')}</p>
<p style='color: #80ed99;'>🏢 运营商：{result.get('server', '未知')}</p>
</div>
            """
            self.phone_result.setHtml(output)
        else:
            self.phone_result.setHtml(f"<span style='color: #ff6b6b;'>{result}</span>")

    def phone_search_error(self, error):
        self.phone_btn.setEnabled(True)
        self.phone_btn.setText("查询")
        self.phone_result.setHtml(f"<span style='color: #ff6b6b;'>错误：{error}</span>")

    def create_idcard_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("🪪 身份证查询")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d9ff;")
        layout.addWidget(title)

        desc = QLabel("输入身份证号码，查询持有人的性别、出生日期和生源地")
        desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(desc)

        layout.addSpacing(10)

        input_layout = QHBoxLayout()
        self.idcard_input = QLineEdit()
        self.idcard_input.setPlaceholderText("请输入身份证号码，例如：360421200501175568")
        input_layout.addWidget(self.idcard_input)

        self.idcard_btn = QPushButton("查询")
        self.idcard_btn.setFixedWidth(100)
        self.idcard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.idcard_btn.clicked.connect(self.do_idcard_search)
        input_layout.addWidget(self.idcard_btn)
        layout.addLayout(input_layout)

        self.idcard_result = self.create_result_text()
        layout.addWidget(self.idcard_result)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def do_idcard_search(self):
        id_num = self.idcard_input.text().strip()
        if not id_num:
            self.idcard_result.setHtml("<span style='color: #ff6b6b;'>请输入有效的身份证号码</span>")
            return

        self.idcard_btn.setEnabled(False)
        self.idcard_btn.setText("查询中...")
        self.idcard_result.setHtml("<span style='color: #ffd93d;'>正在查询，请稍候...</span>")

        self.idcard_worker = Worker(idCard, id_num)
        self.idcard_worker.finished.connect(self.idcard_search_finished)
        self.idcard_worker.error.connect(self.idcard_search_error)
        self.idcard_worker.start()

    def idcard_search_finished(self, result):
        self.idcard_btn.setEnabled(True)
        self.idcard_btn.setText("查询")
        if isinstance(result, dict) and result:
            output = f"""
<div style='line-height: 1.8;'>
<p style='color: #00d9ff; font-size: 16px;'>⚧ 性别：{result.get('gender', '未知')}</p>
<p style='color: #80ed99;'>📅 出生日期：{result.get('birth', '未知')}</p>
<p style='color: #ffd93d;'>🏠 生源地：{result.get('birth_loc', '未知')}</p>
</div>
            """
            self.idcard_result.setHtml(output)
        else:
            self.idcard_result.setHtml(f"<span style='color: #ff6b6b;'>查询失败或未找到该身份证信息</span>")

    def idcard_search_error(self, error):
        self.idcard_btn.setEnabled(True)
        self.idcard_btn.setText("查询")
        self.idcard_result.setHtml(f"<span style='color: #ff6b6b;'>错误：{error}</span>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())