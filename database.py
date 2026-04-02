import sqlite3
from datetime import date

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    is_premium INTEGER DEFAULT 0,
    rename_count INTEGER DEFAULT 0,
    last_reset TEXT,
    thumb TEXT
)
""")
conn.commit()


def get_user(user_id):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    if not user:
        cur.execute("INSERT INTO users (user_id, last_reset) VALUES (?, ?)",
                    (user_id, str(date.today())))
        conn.commit()
        return get_user(user_id)

    return user


def update_count(user_id):
    today = str(date.today())
    user = get_user(user_id)

    if user[3] != today:
        cur.execute("UPDATE users SET rename_count=0, last_reset=? WHERE user_id=?",
                    (today, user_id))
        conn.commit()

    cur.execute("UPDATE users SET rename_count = rename_count + 1 WHERE user_id=?",
                (user_id,))
    conn.commit()


def can_rename(user_id, amount, limit):
    user = get_user(user_id)
    is_premium = user[1]
    count = user[2]

    if is_premium:
        return True

    return count + amount <= limit


def set_thumb(user_id, file_id):
    cur.execute("UPDATE users SET thumb=? WHERE user_id=?", (file_id, user_id))
    conn.commit()


def get_thumb(user_id):
    cur.execute("SELECT thumb FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone()[0] 
