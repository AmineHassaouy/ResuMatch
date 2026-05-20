import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _setup_nltk():
    try:
        import nltk, ssl
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        for category, name in [('tokenizers', 'punkt_tab'), ('corpora', 'stopwords')]:
            try:
                nltk.data.find(f'{category}/{name}')
            except LookupError:
                nltk.download(name, quiet=True)
    except ImportError:
        pass


if __name__ == '__main__':
    _setup_nltk()

    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont
    import database
    from ui.main_window import MainWindow

    database.init_db()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont('Segoe UI', 10))

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
