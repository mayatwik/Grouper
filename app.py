import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///grouper.db")

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
    return apology("need to do it")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

        # Redirect user to home page
        return redirect("/register2")

    else:
        return render_template("register1.html")

@app.route("/register2", methods=["GET", "POST"])
def register2():
    return apology("todo")

@app.route("/register3", methods=["GET", "POST"])
def register3():
    return apology("todo")

if __name__ == '__main__':
    app.run(debug=True)