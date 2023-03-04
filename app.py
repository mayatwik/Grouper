import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date
import requests 
import shutil
import pathlib

from helpers import apology, login_required, blob, convert

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///grouper.db")

UPLOAD_FOLDER = 'static/images/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    session["image"] = 'Yes'
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("firstname"):
            return apology("must provide firstname", 403)

        # Ensure username was submitted
        if not request.form.get("lastname"):
            return apology("must provide lastname", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE first_name = ? AND last_name = ?", request.form.get("firstname"), request.form.get("lastname"))
        # Ensure username exists and password is correct
        print(rows)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["first_name"] = rows[0]["first_name"]
        session["last_name"] = rows[0]["last_name"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("firstname"):
            return apology("must provide first name", 403)

    
        # Ensure password was submitted
        elif not request.form.get("lastname"):
            return apology("must provide Last Name", 403)

        elif not request.form.get("passport"):
            return apology("must provide Passport", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM passports WHERE passport = ?", request.form.get("passport"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not rows[0]["first_name"] == request.form.get("firstname")  or not rows[0]["last_name"] == request.form.get("lastname"):
            return apology("invalid name and/or passport", 403)

        session["passport"] = rows[0]["passport"]
        session["first_name"] = rows[0]["first_name"]
        session["last_name"] = rows[0]["last_name"]

        # Redirect user to register 2
        return redirect("/register2")

    else:
        session.clear()

        return render_template("register1.html")

@app.route("/register2", methods=["GET", "POST"])
def register2():
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        if not "@" in request.form.get("email"):
            return apology("invaild email", 403)

        # Ensure phone number was submitted
        elif not request.form.get("phone"):
            return apology("must provide phone number", 403)

        elif not request.form.get("Harvard_id"):
            return apology("must provide Harvard Student Id", 403)
        
        print(session.get("first_name"))
        print(session.get("password"))

        rows = db.execute("SELECT * FROM harvard WHERE id = ?", int(request.form.get("Harvard_id")))
        print(rows)

        if len(rows) != 1 or not rows[0]["first_name"] == session.get("first_name")  or not rows[0]["last_name"] == session.get("last_name"):
            return apology("must provide a vaild Harvard Student Id", 403)

        # Ensure birthday was submitted
        elif not request.form.get("birthday"):
            return apology("must provide Birthday", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password 2 was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 403)


        if not request.form.get("confirmation") == request.form.get("password"):
            return apology("The passwords don't match", 403)

        password = request.form.get("password")

        db.execute("INSERT INTO users (Harvard_id, hash, birthday, email, phone_number, first_name, last_name, passport) VALUES (?,?,?,?,?,?,?,?)",
            int(request.form.get("Harvard_id")), generate_password_hash(password), request.form.get("birthday"), request.form.get("email"),
            int(request.form.get("phone")), session.get("first_name"), session.get("last_name"),int(session.get("passport")))
        
        # Redirect user to home page
        return redirect("/register3")

    else:
        return render_template("register2.html")

@app.route("/register3", methods=["GET", "POST"])
def register3():
    if request.method == "POST":
        file = request.files['file']
        if file.filename == '':
            return apology("No image selected")
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(session.get("passport"))
        db.execute("UPDATE users SET file = ? WHERE passport = ?", filename, int(session.get("passport")))
        session["image"] = 'Yes'
        return redirect('/')
    else:
        return render_template("register3.html")


if __name__ == '__main__':
    app.run(debug=True)