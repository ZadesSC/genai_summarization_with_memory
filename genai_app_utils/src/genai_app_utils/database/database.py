import sqlite3
import logging

import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAPER_DB_NAME = 'daily_papers.db'

def create_database():
    """Create a SQLite database and table for storing papers."""
    conn = sqlite3.connect(PAPER_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        abstract TEXT
    )
    ''')
    conn.commit()
    conn.close()


def insert_paper(paper):
    """Insert paper data into the database."""
    conn = sqlite3.connect(PAPER_DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO papers (id, title, link, abstract)
        VALUES (?, ?, ?, ?)
        ''', (paper['id'], paper['title'], paper['link'], paper.get('abstract', '')))
        conn.commit()
    except sqlite3.IntegrityError:
        logging.error(f"Paper with ID {paper['id']} already exists in the database.")
    conn.close()


def get_all_papers():
    """Query and display all papers from the database."""
    conn = sqlite3.connect(PAPER_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM papers')
    rows = cursor.fetchall()
    papers = []
    for row in rows:
        paper = {
            'id': row[0],
            'title': row[1],
            'link': row[2],
            'abstract': row[3]
        }
        papers.append(paper)
    conn.close()
    return papers
