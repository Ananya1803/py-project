from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import bcrypt
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="13.57.240.234",
    user="usertest",
    password="Makemein#007",
    database="ananya"
)

@app.route('/')
def index():
    return render_template('index.html', login_error="", register_error="", forgot_password_error="")

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            login_error = "Invalid login credentials"

    return render_template('index.html', login_error=login_error, register_error="", forgot_password_error="")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            register_error = "Email already exists. Please use a different email."
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            db.commit()
            cursor.close()
            return "Registration successful!"

    return render_template('register.html', login_error="", register_error="", forgot_password_error="")

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    username = cursor.fetchone()[0]
    cursor.close()

    return render_template('dashboard.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Generate reset token and store it in the database
        reset_token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
        cursor = db.cursor()
        cursor.execute("INSERT INTO reset_tokens (email, token) VALUES (%s, %s)", (email, reset_token))
        db.commit()
        cursor.close()

        # Send reset email (implement this logic)
        # Include a link to the reset password page, passing the reset_token as a URL parameter

        return "Password reset instructions sent to your email."

    return render_template('forgot_password.html', login_error="", register_error="", forgot_password_error="")

if __name__ == '__main__':
    app.run(debug=True)
