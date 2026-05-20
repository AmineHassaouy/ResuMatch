import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resumatch.db')


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            required_skills TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_name TEXT,
            resume_filename TEXT,
            extracted_text TEXT,
            score REAL,
            matched_skills TEXT,
            unmatched_skills TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    ''')
    conn.commit()
    conn.close()


def create_job(title, description, required_skills):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO jobs (title, description, required_skills, created_at) VALUES (?, ?, ?, ?)',
        (title, description, required_skills, datetime.now().isoformat()),
    )
    job_id = c.lastrowid
    conn.commit()
    conn.close()
    return job_id


def get_all_jobs():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows


def get_job(job_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = c.fetchone()
    conn.close()
    return row


def save_application(job_id, candidate_name, resume_filename,
                     extracted_text, score, matched_skills, unmatched_skills):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        '''INSERT INTO applications
           (job_id, candidate_name, resume_filename, extracted_text,
            score, matched_skills, unmatched_skills, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (job_id, candidate_name, resume_filename, extracted_text,
         score, matched_skills, unmatched_skills, datetime.now().isoformat()),
    )
    app_id = c.lastrowid
    conn.commit()
    conn.close()
    return app_id
