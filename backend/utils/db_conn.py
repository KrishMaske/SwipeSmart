import sqlite3
from config.settings import DB_PATH
from contextlib import contextmanager

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        yield c
        conn.commit()
    finally:
        conn.close()