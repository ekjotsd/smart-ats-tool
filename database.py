import sqlite3

# --- Connect to SQLite and return cursor + connection ---
def get_db_connection():
    conn = sqlite3.connect("smart_ats.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialize the DB with users table ---
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Insert test users ---
def insert_sample_users():
    users = [
        ("applicant", "applicant@yopmail.com", "password123", "Applicant"),
        ("recruiter", "recruiter@yopmail.com", "password123", "Recruiter"),
        ("company", "company@yopmail.com", "password123", "Hiring Company")
    ]
    conn = get_db_connection()
    cursor = conn.cursor()
    for user in users:
        try:
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", user)
        except sqlite3.IntegrityError:
            continue  # Skip if user already exists
    conn.commit()
    conn.close()

# --- Validate user login ---
def validate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user
