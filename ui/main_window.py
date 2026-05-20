from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.jobs_page import JobsPage


SIDEBAR_STYLE = '''
    QFrame#sidebar {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    QLabel#appName {
        color: #F8FAFC;
        font-size: 18px;
        font-weight: bold;
    }
    QLabel#appSub {
        color: #64748B;
        font-size: 11px;
    }
    QFrame#sidebarDiv {
        background-color: #334155;
        max-height: 1px;
    }
    QLabel#navSection {
        color: #475569;
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    QPushButton#navBtn {
        text-align: left;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 13px;
        border: none;
        color: #94A3B8;
        background: transparent;
    }
    QPushButton#navBtn:checked {
        background-color: #2563EB;
        color: #FFFFFF;
    }
    QPushButton#navBtn:hover:!checked {
        background-color: #334155;
        color: #E2E8F0;
    }
    QLabel#sidebarVersion {
        color: #334155;
        font-size: 11px;
    }
'''


class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('sidebar')
        self.setFixedWidth(220)
        self.setStyleSheet(SIDEBAR_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Brand
        brand = QWidget()
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(20, 24, 20, 20)
        bl.setSpacing(2)
        name = QLabel('ResuMatch')
        name.setObjectName('appName')
        sub = QLabel('Matching de CV')
        sub.setObjectName('appSub')
        bl.addWidget(name)
        bl.addWidget(sub)
        root.addWidget(brand)

        div = QFrame()
        div.setObjectName('sidebarDiv')
        div.setFixedHeight(1)
        root.addWidget(div)

        # Nav
        nav = QWidget()
        nl = QVBoxLayout(nav)
        nl.setContentsMargins(12, 16, 12, 16)
        nl.setSpacing(4)

        sec = QLabel('NAVIGATION')
        sec.setObjectName('navSection')
        nl.addWidget(sec)

        self.jobs_btn = QPushButton('  Offres d\'emploi')
        self.jobs_btn.setObjectName('navBtn')
        self.jobs_btn.setCheckable(True)
        self.jobs_btn.setChecked(True)
        nl.addWidget(self.jobs_btn)
        nl.addStretch()
        root.addWidget(nav)
        root.addStretch()

        ver = QLabel('v1.0.0')
        ver.setObjectName('sidebarVersion')
        ver.setAlignment(Qt.AlignCenter)
        ver.setContentsMargins(0, 0, 0, 12)
        root.addWidget(ver)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ResuMatch')
        self.setMinimumSize(1000, 660)
        self.resize(1200, 800)
        self.setStyleSheet('QMainWindow { background: #F1F5F9; }')
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet('QStackedWidget { background: #F1F5F9; }')
        self.jobs_page = JobsPage()
        self.stack.addWidget(self.jobs_page)
        root.addWidget(self.stack)

        self.sidebar.jobs_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.jobs_page)
        )
