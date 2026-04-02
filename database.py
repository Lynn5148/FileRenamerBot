import sqlite3
from datetime import datetime

conn = sqlite3.connect("queue.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT,
    video TEXT,
    link TEXT,
    name TEXT,
    company TEXT,
    thumb TEXT,
    post_time REAL,
    status TEXT
)
""")
conn.commit()


def add_post(data):
    cur.execute("""
    INSERT INTO posts (mode, video, link, name, company, thumb, post_time, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()


def get_pending():
    cur.execute("SELECT * FROM posts WHERE status='pending'")
    return cur.fetchall()


def mark_done(post_id):
    cur.execute("UPDATE posts SET status='done' WHERE id=?", (post_id,))
    conn.commit()


def get_last_time():
    cur.execute("SELECT post_time FROM posts ORDER BY post_time DESC LIMIT 1")
    res = cur.fetchone()
    return res[0] if res else None
