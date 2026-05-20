import re
import os


def extract_text_from_pdf(filepath):
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
        return '\n'.join(parts)
    except Exception:
        return ''


def extract_text_from_docx(filepath):
    try:
        from docx import Document
        doc = Document(filepath)
        return '\n'.join(p.text for p in doc.paragraphs)
    except Exception:
        return ''


def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    if ext in ('.docx', '.doc'):
        return extract_text_from_docx(filepath)
    return ''


def preprocess_text(text):
    lowered = text.lower()
    # Keep alphanumeric and chars common in tech skill names (+, #, ., -)
    cleaned = re.sub(r'[^\w\s+#.\-]', ' ', lowered)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        tokens = word_tokenize(cleaned, language='french')
        stop_fr = set(stopwords.words('french'))
        # Preserve tokens that look like tech skills (non-purely-alpha or short)
        filtered = [t for t in tokens if t not in stop_fr or not t.isalpha()]
        return ' '.join(filtered)
    except Exception:
        return cleaned


def extract_candidate_name(text):
    for line in text.strip().splitlines()[:8]:
        line = line.strip()
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return line
    return 'Candidat'
