import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QFont

import database
import resume_parser
import skill_matcher

STYLE = '''
    QPushButton#backBtn {
        background: transparent;
        color: #2563EB;
        border: none;
        font-size: 13px;
        font-weight: bold;
        padding: 6px 0;
        text-align: left;
    }
    QPushButton#backBtn:hover { color: #1D4ED8; }

    QFrame#card {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    QLabel#jobTitle { color: #1E293B; }
    QLabel#jobDesc  { color: #64748B; font-size: 13px; }
    QLabel#sectionLbl {
        color: #64748B;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    QLabel#sectionTitle { color: #1E293B; font-size: 15px; font-weight: bold; }
    QLabel#reqTag {
        background: #EFF6FF;
        color: #2563EB;
        border-radius: 5px;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: bold;
    }

    QFrame#uploadZone {
        background: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
    }
    QFrame#uploadZone:hover {
        border-color: #2563EB;
        background: #EFF6FF;
    }
    QLabel#uploadHint { color: #94A3B8; font-size: 12px; }
    QPushButton#browseBtn {
        background: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 9px 22px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#browseBtn:hover { background: #1D4ED8; }
    QPushButton#browseBtn:disabled { background: #94A3B8; }
    QLabel#progressLbl { color: #2563EB; font-size: 13px; }
    QLabel#errorLbl    { color: #EF4444; font-size: 13px; }

    /* Result card */
    QFrame#resultCard {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    QLabel#candidateName { color: #1E293B; font-size: 16px; font-weight: bold; }
    QLabel#candidateFile { color: #94A3B8; font-size: 12px; }

    QFrame#scoreOk   {
        background: #ECFDF5; border-radius: 44px;
        border: 3px solid #10B981;
    }
    QFrame#scoreKo   {
        background: #FEF2F2; border-radius: 44px;
        border: 3px solid #EF4444;
    }
    QLabel#scoreNum  { color: #1E293B; font-size: 22px; font-weight: bold; }
    QLabel#scoreTxt  { color: #64748B; font-size: 11px; }

    QFrame#verdictOk {
        background: #ECFDF5;
        border-radius: 8px;
        border: 1px solid #6EE7B7;
    }
    QFrame#verdictKo {
        background: #FEF2F2;
        border-radius: 8px;
        border: 1px solid #FCA5A5;
    }
    QLabel#verdictLbl { color: #1E293B; font-size: 13px; font-weight: bold; }

    QFrame#matchedBox {
        background: #F0FDF4;
        border-radius: 10px;
        border: 1px solid #A7F3D0;
    }
    QFrame#unmatchedBox {
        background: #FFF1F2;
        border-radius: 10px;
        border: 1px solid #FECDD3;
    }
    QLabel#boxTitle { color: #374151; font-size: 12px; font-weight: bold; }
    QLabel#tagOk {
        background: #D1FAE5; color: #065F46;
        border-radius: 4px; padding: 3px 10px;
        font-size: 11px; font-weight: bold;
    }
    QLabel#tagKo {
        background: #FFE4E6; color: #9F1239;
        border-radius: 4px; padding: 3px 10px;
        font-size: 11px; font-weight: bold;
    }
'''


class _ParseWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, filepath, job_id):
        super().__init__()
        self.filepath = filepath
        self.job_id = job_id

    def run(self):
        try:
            job = database.get_job(self.job_id)
            required_skills = job[3]

            raw = resume_parser.extract_text(self.filepath)
            if not raw.strip():
                self.error.emit('Impossible d\'extraire le texte du fichier.')
                return

            processed = resume_parser.preprocess_text(raw)
            name = resume_parser.extract_candidate_name(raw)
            score, matched, unmatched = skill_matcher.match_skills(processed, required_skills)

            database.save_application(
                self.job_id, name, os.path.basename(self.filepath),
                raw[:3000], score, ','.join(matched), ','.join(unmatched),
            )

            self.finished.emit({
                'candidate_name': name,
                'filename': os.path.basename(self.filepath),
                'score': score,
                'matched': matched,
                'unmatched': unmatched,
                'compatible': skill_matcher.is_compatible(score),
            })
        except Exception as exc:
            self.error.emit(str(exc))


def _skill_tags_widget(skills, tag_name):
    w = QWidget()
    outer = QVBoxLayout(w)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(4)
    row = None
    for i, skill in enumerate(skills):
        if i % 5 == 0:
            if row is not None:
                row.addStretch()
            row = QHBoxLayout()
            row.setSpacing(6)
            outer.addLayout(row)
        tag = QLabel(skill)
        tag.setObjectName(tag_name)
        row.addWidget(tag)
    if row is not None:
        row.addStretch()
    return w


class _ResultWidget(QFrame):
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setObjectName('resultCard')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        compatible = result['compatible']
        score = result['score']

        # Header: name + score circle
        header = QHBoxLayout()

        left = QVBoxLayout()
        left.setSpacing(2)
        name_lbl = QLabel(result.get('candidate_name', 'Candidat'))
        name_lbl.setObjectName('candidateName')
        file_lbl = QLabel(result.get('filename', ''))
        file_lbl.setObjectName('candidateFile')
        left.addWidget(name_lbl)
        left.addWidget(file_lbl)
        header.addLayout(left)
        header.addStretch()

        badge = QFrame()
        badge.setObjectName('scoreOk' if compatible else 'scoreKo')
        badge.setFixedSize(88, 88)
        bl = QVBoxLayout(badge)
        bl.setAlignment(Qt.AlignCenter)
        bl.setSpacing(0)
        num = QLabel(f'{int(score)}%')
        num.setObjectName('scoreNum')
        num.setAlignment(Qt.AlignCenter)
        bl.addWidget(num)
        txt = QLabel('Score')
        txt.setObjectName('scoreTxt')
        txt.setAlignment(Qt.AlignCenter)
        bl.addWidget(txt)
        header.addWidget(badge)
        layout.addLayout(header)

        # Verdict banner
        verdict = QFrame()
        verdict.setObjectName('verdictOk' if compatible else 'verdictKo')
        vl = QHBoxLayout(verdict)
        vl.setContentsMargins(16, 10, 16, 10)
        symbol = '[OK]' if compatible else '[X]'
        text = 'Compatible avec ce poste' if compatible else 'Non compatible avec ce poste'
        vlbl = QLabel(f'{symbol}  {text}')
        vlbl.setObjectName('verdictLbl')
        vl.addWidget(vlbl)
        layout.addWidget(verdict)

        # Skills breakdown
        row = QHBoxLayout()
        row.setSpacing(12)

        if result['matched']:
            box = QFrame()
            box.setObjectName('matchedBox')
            bl2 = QVBoxLayout(box)
            bl2.setContentsMargins(14, 12, 14, 12)
            bl2.setSpacing(8)
            title = QLabel(f'Competences trouvees ({len(result["matched"])})')
            title.setObjectName('boxTitle')
            bl2.addWidget(title)
            bl2.addWidget(_skill_tags_widget(result['matched'], 'tagOk'))
            row.addWidget(box)

        if result['unmatched']:
            box2 = QFrame()
            box2.setObjectName('unmatchedBox')
            bl3 = QVBoxLayout(box2)
            bl3.setContentsMargins(14, 12, 14, 12)
            bl3.setSpacing(8)
            title2 = QLabel(f'Competences manquantes ({len(result["unmatched"])})')
            title2.setObjectName('boxTitle')
            bl3.addWidget(title2)
            bl3.addWidget(_skill_tags_widget(result['unmatched'], 'tagKo'))
            row.addWidget(box2)

        layout.addLayout(row)


class JobDetailPage(QWidget):
    back_requested = Signal()

    def __init__(self, job_id, parent=None):
        super().__init__(parent)
        self.job_id = job_id
        self.job_data = database.get_job(job_id)
        self._thread = None
        self._worker = None
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 32)
        root.setSpacing(20)

        # Back button
        back_row = QHBoxLayout()
        back_btn = QPushButton('<  Retour aux offres')
        back_btn.setObjectName('backBtn')
        back_btn.clicked.connect(self.back_requested.emit)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        root.addLayout(back_row)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet('QScrollArea { background: transparent; }')

        content = QWidget()
        content.setStyleSheet('QWidget { background: transparent; }')
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 12, 0)
        cl.setSpacing(20)

        # Job info card
        job_card = QFrame()
        job_card.setObjectName('card')
        jl = QVBoxLayout(job_card)
        jl.setContentsMargins(24, 20, 24, 20)
        jl.setSpacing(10)

        title_lbl = QLabel(self.job_data[1])
        title_lbl.setObjectName('jobTitle')
        f = QFont()
        f.setPointSize(18)
        f.setBold(True)
        title_lbl.setFont(f)
        jl.addWidget(title_lbl)

        if self.job_data[2]:
            desc_lbl = QLabel(self.job_data[2])
            desc_lbl.setObjectName('jobDesc')
            desc_lbl.setWordWrap(True)
            jl.addWidget(desc_lbl)

        skills_lbl = QLabel('COMPETENCES REQUISES')
        skills_lbl.setObjectName('sectionLbl')
        jl.addWidget(skills_lbl)

        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)
        for skill in [s.strip() for s in self.job_data[3].split(',') if s.strip()]:
            tag = QLabel(skill)
            tag.setObjectName('reqTag')
            tags_row.addWidget(tag)
        tags_row.addStretch()
        jl.addLayout(tags_row)
        cl.addWidget(job_card)

        # Upload card
        upload_card = QFrame()
        upload_card.setObjectName('card')
        ul = QVBoxLayout(upload_card)
        ul.setContentsMargins(24, 20, 24, 20)
        ul.setSpacing(14)

        sec_title = QLabel('Analyser un CV')
        sec_title.setObjectName('sectionTitle')
        ul.addWidget(sec_title)

        # Drop zone
        zone = QFrame()
        zone.setObjectName('uploadZone')
        zone.setMinimumHeight(130)
        zl = QVBoxLayout(zone)
        zl.setAlignment(Qt.AlignCenter)
        zl.setSpacing(8)

        upload_lbl = QLabel('Selectionnez un fichier PDF ou DOCX')
        upload_lbl.setObjectName('uploadHint')
        upload_lbl.setAlignment(Qt.AlignCenter)
        zl.addWidget(upload_lbl)

        self.browse_btn = QPushButton('Parcourir...')
        self.browse_btn.setObjectName('browseBtn')
        self.browse_btn.clicked.connect(self._pick_file)
        zl.addWidget(self.browse_btn, 0, Qt.AlignCenter)
        ul.addWidget(zone)

        self.status_lbl = QLabel('')
        self.status_lbl.setObjectName('progressLbl')
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setVisible(False)
        ul.addWidget(self.status_lbl)

        cl.addWidget(upload_card)

        # Results area (prepend new results at top)
        self.results_lbl = QLabel('Resultats d\'analyse')
        self.results_lbl.setObjectName('sectionTitle')
        self.results_lbl.setVisible(False)
        cl.addWidget(self.results_lbl)

        self.results_layout = QVBoxLayout()
        self.results_layout.setSpacing(12)
        cl.addLayout(self.results_layout)

        cl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll)

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Sélectionner un CV', '', 'Documents (*.pdf *.docx *.doc)'
        )
        if path:
            self._analyze(path)

    def _analyze(self, filepath):
        self.browse_btn.setEnabled(False)
        self.status_lbl.setText(f'Analyse de {os.path.basename(filepath)} en cours...')
        self.status_lbl.setObjectName('progressLbl')
        self.status_lbl.setVisible(True)

        self._thread = QThread()
        self._worker = _ParseWorker(filepath, self.job_id)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_done(self, result):
        self.status_lbl.setVisible(False)
        self.browse_btn.setEnabled(True)
        self.results_lbl.setVisible(True)

        widget = _ResultWidget(result)
        self.results_layout.insertWidget(0, widget)

    def _on_error(self, msg):
        self.status_lbl.setObjectName('errorLbl')
        self.status_lbl.setText(f'Erreur : {msg}')
        self.browse_btn.setEnabled(True)
