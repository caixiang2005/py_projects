import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame, QLabel, QGridLayout, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from main import get_inf, set_option


class CourseCard(QFrame):
    def __init__(self, course_name, location, start_time, duration, color):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 5px;
                border: 1px solid {self.darken_color(color)};
            }}
            QLabel {{
                color: #222;
                font-weight: bold;
                padding: 6px;
                font-size: 13px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        course_label = QLabel(course_name)
        course_label.setWordWrap(True)
        course_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        location_label = QLabel(location)
        location_label.setWordWrap(True)
        location_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(course_label)
        layout.addWidget(location_label)
        self.setLayout(layout)
        
        self.setMinimumHeight(58 * duration)
    
    def darken_color(self, color):
        color_map = {
            "#A8D8EA": "#88C0D0",
            "#AA96DA": "#8E7CC3",
            "#FCBAD3": "#E695BD",
            "#FFFFD2": "#E6E6B8",
            "#A0E7A0": "#80C080",
            "#B5EAD7": "#95CDB5",
            "#FFB7B2": "#E69B97",
        }
        return color_map.get(color, color)


class DataLoadThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.data = None

    def run(self):
        try:
            driver = set_option()
            data = get_inf(driver=driver)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class CourseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("课表查询")
        self.setFixedSize(1200, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.load_button = QPushButton("加载课表数据")
        self.load_button.setFixedHeight(50)
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.load_button.clicked.connect(self.load_data)
        layout.addWidget(self.load_button)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content_widget = QFrame()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.setLayout(self.grid_layout)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)

        self.setLayout(layout)
        
        self.colors = [
            "#A8D8EA", "#AA96DA", "#FCBAD3", "#FFFFD2", 
            "#A0E7A0", "#B5EAD7", "#FFB7B2"
        ]
        
        self.load_thread = None

    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_data(self):
        self.load_button.setText("正在加载数据，请稍候...")
        self.load_button.setEnabled(False)
        
        self.load_thread = DataLoadThread()
        self.load_thread.finished.connect(self.load_finished)
        self.load_thread.error.connect(self.load_error)
        self.load_thread.start()

    def load_finished(self, data):
        if isinstance(data, str):
            QMessageBox.warning(self, "错误", data)
            self.load_button.setText("加载课表数据")
            self.load_button.setEnabled(True)
            return

        self.clear_grid()
        
        header_style = "font-weight: bold; padding: 12px; background-color: #1976D2; color: white; border: 1px solid #0D47A1;"
        cell_style = "background-color: white; border: 1px solid #BDBDBD;"
        row_label_style = "font-weight: bold; padding: 10px; background-color: #E3F2FD; border: 1px solid #90CAF9; color: #1565C0;"
        
        header_label = QLabel("节次")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(header_style)
        self.grid_layout.addWidget(header_label, 0, 0)
        
        days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(header_style)
            self.grid_layout.addWidget(label, 0, i + 1)
        
        for row in range(1, 11):
            row_label = QLabel(str(row))
            row_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_label.setStyleSheet(row_label_style)
            self.grid_layout.addWidget(row_label, row, 0)
            
            for col in range(7):
                cell = QFrame()
                cell.setFixedHeight(58)
                cell.setStyleSheet(cell_style)
                cell_layout = QVBoxLayout()
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(0)
                cell.setLayout(cell_layout)
                self.grid_layout.addWidget(cell, row, col + 1)
        
        color_index = 0
        for day_idx, day in enumerate(days):
            if day in data:
                courses = data[day]
                for i in range(0, len(courses), 4):
                    if i + 3 < len(courses):
                        start_time = courses[i]
                        duration = courses[i + 1]
                        course_name = courses[i + 2]
                        location = courses[i + 3]
                        
                        color = self.colors[color_index % len(self.colors)]
                        card = CourseCard(course_name, location, start_time, duration, color)
                        self.grid_layout.addWidget(card, start_time, day_idx + 1, duration, 1)
                        
                        color_index += 1

        self.load_button.setText("课表加载完成")

    def load_error(self, error_msg):
        QMessageBox.critical(self, "错误", f"加载失败：{error_msg}")
        self.load_button.setText("加载课表数据")
        self.load_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CourseApp()
    window.show()
    sys.exit(app.exec())
