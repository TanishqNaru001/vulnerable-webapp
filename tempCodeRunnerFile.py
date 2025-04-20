from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'insecure_secret'  # Vulnerable: Hardcoded secret key

# Vulnerable: No password hashing
def create_connection():
    return sqlite3.connect('database.db')

# Create tables
with create_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY, user_id INTEGER, filename TEXT)''')

# Vulnerable: No input validation
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        with create_connection() as conn:
            conn.execute(f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{password}')")  # Vulnerable: SQL Injection
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with create_connection() as conn:
            user = conn.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'").fetchone()  # Vulnerable: SQL Injection
            if user:
                session['user_id'] = user[0]  # Vulnerable: Simple session management
                return redirect('/profile')
        return 'Login failed'
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    with create_connection() as conn:
        user = conn.execute(f"SELECT * FROM users WHERE id={session['user_id']}").fetchone()
    return render_template('profile.html', user=user)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            with create_connection() as conn:
                conn.execute(f"INSERT INTO files (user_id, filename) VALUES ({session['user_id']}, '{filename}')")  # Vulnerable: Path traversal possible
            return redirect('/gallery')
    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    if 'user_id' not in session:
        return redirect('/login')
    with create_connection() as conn:
        files = conn.execute(f"SELECT filename FROM files WHERE user_id={session['user_id']}").fetchall()
    return render_template('gallery.html', files=files)

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect('/login')
    new_password = request.form['new_password']
    with create_connection() as conn:
        conn.execute(f"UPDATE users SET password='{new_password}' WHERE id={session['user_id']}")  # Vulnerable: No old password check
    return 'Password changed'

@app.route('/')
def home():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)  # Vulnerable: Debug mode enabled