from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import connect, Error
from mysql.connector.errors import DatabaseError, IntegrityError

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret123')

# Database configuration
def get_db_connection():
    try:
        connection = connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'V8r$9tLq#2pX!mF7'),
            database=os.getenv('DB_NAME', 'restAPI')
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None 

# get user via email
def get_user_by_email(email):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            return user
        except DatabaseError as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

# Flask app configuration 
@app.route("/", methods=['GET'])
def root():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return url_for('login')

# user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        # Minimal validations
        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            #default to 'user'
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name or None, email, hashed_pw),
            )
            conn.commit()
        except IntegrityError:
            conn.rollback()
            # UNIQUE(email) constraint
            flash("That email is already registered.")
            return redirect(url_for("register"))
        finally:
            try:
                cur.close()
            except Exception:
                pass
            conn.close()

        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))

    return url_for("register")

# user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.")
            return redirect(url_for("login"))

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return url_for("login")

# user dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session.get("name"))

# user logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)