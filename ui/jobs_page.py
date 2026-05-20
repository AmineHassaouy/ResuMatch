from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QStackedWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

import database
from ui.job_form_dialog import JobFormDialog
from ui.job_detail_page import JobDetailPage

STYLE = '''
    QWidget#listPage  { background: transparent; }
    QLabel#pageTitle  { color: #1E293B; }
    QLabel#pageSub    { color: #64748B; font-size: 13px; }

    QPushButton#newBtn {
        background: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#newBtn:hover   { background: #1D4ED8; }
    QPushButton#newBtn:pressed { background: #1E40AF; }

    QScrollArea         { background: transparent; border: none; }
    QScrollArea > QWidget > QWidget { background: transparent; }

    QFrame#jobCard {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    QFrame#jobCard:hover {
        border-color: #93C5FD;
        background: #F8FAFC;
    }
    QLabel#cardTitle { color: #1E293B; font-size: 14px; font-weight: bold; }
    QLabel#cardDate  { color: #94A3B8; font-size: 11px; }
    QLabel#cardDesc  { color: #64748B; font-size: 12px; }
    QLabel#cardTag {
        background: #EFF6FF;
        color: #2563EB;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
    }
    QLabel#cardTagMore {
        background: #F1F5F9;
        color: #64748B;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
    }
    QLabel#emptyState {
        color: #94A3B8;
        font-size: 14px;
    }
'''


class _JobCard(QFrame):
    clicked = Signal(int)

    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.job_id = job_data[0]
        self.setObjectName('jobCard')
        self.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Title row
        hdr = QHBoxLayout()
        title = QLabel(job_data[1])
        title.setObjectName('cardTitle')
        hdr.addWidget(title)
        hdr.addStretch()
        date_str = (job_data[4] or '')[:10]
        date_lbl = QLabel(date_str)
        date_lbl.setObjectName('cardDate')
        hdr.addWidget(date_lbl)
        layout.addLayout(hdr)

        # Description preview
        desc = (job_data[2] or '').strip()
        if desc:
            preview = desc[:130] + ('...' if len(desc) > 130 else '')
            desc_lbl = QLabel(preview)
            desc_lbl.setObjectName('cardDesc')
            desc_lbl.setWordWrap(True)
            layout.addWidget(desc_lbl)

        # Skill tags
        skills = [s.strip() for s in (job_data[3] or '').split(',') if s.strip()]
        if skills:
            tags_row = QHBoxLayout()
            tags_row.setSpacing(5)
            for skill in skills[:6]:
                tag = QLabel(skill)
                tag.setObjectName('cardTag')
                tags_row.addWidget(tag)
            if len(skills) > 6:
                more = QLabel(f'+{len(skills) - 6}')
                more.setObjectName('cardTagMore')
                tags_row.addWidget(more)
            tags_row.addStretch()
            layout.addLayout(tags_row)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.job_id)
        super().mousePressEvent(event)


class JobsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet('QStackedWidget { background: #F1F5F9; }')
        root.addWidget(self._stack)

        # Page 0 — list
        self._list_page = QWidget()
        self._list_page.setObjectName('listPage')
        self._build_list_page()
        self._stack.addWidget(self._list_page)

        self._detail_page = None

    def _build_list_page(self):
        layout = QVBoxLayout(self._list_page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel('Offres d\'emploi')
        title.setObjectName('pageTitle')
        f = QFont()
        f.setPointSize(22)
        f.setBold(True)
        title.setFont(f)
        hdr.addWidget(title)
        hdr.addStretch()
        new_btn = QPushButton('+ Nouvelle offre')
        new_btn.setObjectName('newBtn')
        new_btn.clicked.connect(self._open_new_job_dialog)
        hdr.addWidget(new_btn)
        layout.addLayout(hdr)

        sub = QLabel('Gérez vos offres et analysez les candidatures')
        sub.setObjectName('pageSub')
        layout.addWidget(sub)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet('background: transparent;')
        self._cards_layout = QVBoxLayout(self._scroll_content)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(12)
        self._cards_layout.addStretch()

        scroll.setWidget(self._scroll_content)
        layout.addWidget(scroll)

        self._load_jobs()

    def _load_jobs(self):
        # Remove all items except the trailing stretch
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        jobs = database.get_all_jobs()
        if not jobs:
            empty = QLabel('Aucune offre créée.  Cliquez sur « + Nouvelle offre » pour commencer.')
            empty.setObjectName('emptyState')
            empty.setAlignment(Qt.AlignCenter)
            self._cards_layout.insertWidget(0, empty)
        else:
            for job in jobs:
                card = _JobCard(job)
                card.clicked.connect(self._open_job_detail)
                self._cards_layout.insertWidget(
                    self._cards_layout.count() - 1, card
                )

    def _open_new_job_dialog(self):
        dlg = JobFormDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._load_jobs()

    def _open_job_detail(self, job_id):
        if self._detail_page is not None:
            self._stack.removeWidget(self._detail_page)
            self._detail_page.deleteLater()

        self._detail_page = JobDetailPage(job_id)
        self._detail_page.back_requested.connect(self._show_list)
        self._stack.addWidget(self._detail_page)
        self._stack.setCurrentWidget(self._detail_page)

    def _show_list(self):
        self._load_jobs()
        self._stack.setCurrentWidget(self._list_page)
