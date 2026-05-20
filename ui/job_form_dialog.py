from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import database

STYLE = '''
    QDialog {
        background: #FFFFFF;
    }
    QLabel#dlgTitle {
        color: #1E293B;
        font-size: 16px;
        font-weight: bold;
    }
    QLabel#dlgSub {
        color: #64748B;
        font-size: 13px;
    }
    QFrame#dlgDiv {
        background: #E2E8F0;
        max-height: 1px;
    }
    QLabel#fieldLabel {
        color: #374151;
        font-size: 12px;
        font-weight: bold;
    }
    QLabel#fieldHint {
        color: #94A3B8;
        font-size: 11px;
    }
    QLineEdit {
        border: 1.5px solid #E2E8F0;
        border-radius: 8px;
        padding: 9px 13px;
        font-size: 13px;
        color: #1E293B;
        background: #F8FAFC;
    }
    QLineEdit:focus {
        border-color: #2563EB;
        background: #FFFFFF;
    }
    QTextEdit {
        border: 1.5px solid #E2E8F0;
        border-radius: 8px;
        padding: 9px 13px;
        font-size: 13px;
        color: #1E293B;
        background: #F8FAFC;
    }
    QTextEdit:focus {
        border-color: #2563EB;
        background: #FFFFFF;
    }
    QPushButton#saveBtn {
        background: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 28px;
        font-size: 13px;
        font-weight: bold;
        min-width: 140px;
    }
    QPushButton#saveBtn:hover { background: #1D4ED8; }
    QPushButton#saveBtn:pressed { background: #1E40AF; }
    QPushButton#cancelBtn {
        background: transparent;
        color: #64748B;
        border: 1.5px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 13px;
    }
    QPushButton#cancelBtn:hover {
        background: #F1F5F9;
        color: #1E293B;
    }
'''


class JobFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Nouvelle offre d\'emploi')
        self.setMinimumWidth(560)
        self.setModal(True)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_lbl = QLabel('Créer une nouvelle offre')
        title_lbl.setObjectName('dlgTitle')
        layout.addWidget(title_lbl)

        sub_lbl = QLabel('Remplissez les informations de l\'offre d\'emploi')
        sub_lbl.setObjectName('dlgSub')
        layout.addWidget(sub_lbl)

        div = QFrame()
        div.setObjectName('dlgDiv')
        div.setFixedHeight(1)
        layout.addWidget(div)

        layout.addWidget(self._label('Titre du poste *'))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText('ex : Développeur Python Senior')
        layout.addWidget(self.title_edit)

        layout.addWidget(self._label('Description du poste'))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText(
            'Décrivez les responsabilités et le contexte du poste...'
        )
        self.desc_edit.setMinimumHeight(100)
        self.desc_edit.setMaximumHeight(140)
        layout.addWidget(self.desc_edit)

        layout.addWidget(self._label('Compétences requises *'))
        hint = QLabel('Séparez les compétences par des virgules  —  ex : Python, Django, SQL, Docker')
        hint.setObjectName('fieldHint')
        layout.addWidget(hint)
        self.skills_edit = QLineEdit()
        self.skills_edit.setPlaceholderText('Python, Django, SQL, Docker, Git...')
        layout.addWidget(self.skills_edit)

        layout.addSpacing(8)

        btns = QHBoxLayout()
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setObjectName('cancelBtn')
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        btns.addStretch()
        save_btn = QPushButton('Créer l\'offre')
        save_btn.setObjectName('saveBtn')
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName('fieldLabel')
        return lbl

    def _save(self):
        title = self.title_edit.text().strip()
        desc = self.desc_edit.toPlainText().strip()
        skills = self.skills_edit.text().strip()

        if not title:
            QMessageBox.warning(self, 'Champ requis', 'Le titre du poste est obligatoire.')
            return
        if not skills:
            QMessageBox.warning(self, 'Champ requis', 'Veuillez saisir au moins une compétence.')
            return

        database.create_job(title, desc, skills)
        self.accept()
