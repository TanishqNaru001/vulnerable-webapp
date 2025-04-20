from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'insecure_secret_key'  # Security issue

# Database connection
def create_connection():
    return sqlite3.connect('database.db')

# Initialize database
with create_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY, user_id INTEGER, filename TEXT)''')

# Routes
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        with create_connection() as conn:
            conn.execute(f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{password}')")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with create_connection() as conn:
            user = conn.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'").fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect('/profile')
        return 'Invalid credentials'
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
            filename = file.filename.replace(' ', '_')  # Basic sanitization
            file.save(os.path.join('uploads', filename))
            with create_connection() as conn:
                conn.execute(f"INSERT INTO files (user_id, filename) VALUES ({session['user_id']}, '{filename}')")
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
        conn.execute(f"UPDATE users SET password='{new_password}' WHERE id={session['user_id']}")
    return 'Password changed successfully'

@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory('uploads', filename)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    # Create uploads directory if not exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)