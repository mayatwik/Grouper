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
from bs4 import BeautifulSoup

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

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        id_event = request.form.get("event_id")
        event = db.execute("SELECT * FROM events WHERE id = ?", id_event)
        id_person = db.execute("SELECT id FROM users WHERE passport = ?", int(session.get("passport")))[0]["id"]
        registers = db.execute("SELECT id_person FROM registers WHERE id_event = ?", id_event)
        print(registers)
        for register in registers:
            if register["id_person"] ==  id_person:
                return apology("I'm sorry, you have already registered to that event! see you there!")
        if event[0]["people_number"]:
            limit = event[0]["people_number"]
            amount = db.execute("SELECT COUNT(*) FROM registers JOIN events ON events.id = registers.id_event WHERE id = ?", id_event)[0]["COUNT(*)"]
            if int(limit) == int(amount):
                return apology("all the places are taken! sorry! :(")
        db.execute("INSERT INTO registers (id_person, id_event) VALUES (?,?)", id_person, id_event)
        return redirect('/')
    else:
        registers = []
        id_person = db.execute("SELECT id FROM users WHERE passport = ?", int(session.get("passport")))[0]["id"]

        registers_fake = db.execute("SELECT id_event FROM registers WHERE id_person = ?", id_person)
        for register in registers_fake:
            registers.append(str(register["id_event"]))
        events = db.execute("SELECT * FROM events")
        return render_template("homepage.html", events=events, registers=registers)

@app.route('/profile2',  methods=["GET", "POST"])
@login_required
def profile2():
    if request.method == "POST":
        print(request.form.get("passport"))
        person = db.execute("SELECT * FROM users WHERE passport = ?",int(request.form.get("passport")))
        print(person)
        image = db.execute("SELECT file FROM users WHERE passport = ?", int(request.form.get("passport")))[0]["file"]
         
        return render_template("profile.html", first_name = person[0]["first_name"], last_name = person[0]["last_name"],
        birthday = person[0]["birthday"], image = str(image), bio = person[0]["bio"], gender= person[0]["gender"], country = person[0]["country"])
    else:
        return render_template("hopepage.html")
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        return apology("")
    else:

        person = db.execute("SELECT * FROM users WHERE passport = ?", int(session.get("passport")))
        image = db.execute("SELECT file FROM users WHERE passport = ?", int(session.get("passport")))[0]["file"]
         
        return render_template("profile.html", first_name = person[0]["first_name"], last_name = person[0]["last_name"],
        birthday = person[0]["birthday"], image = image, bio = person[0]["bio"], gender= person[0]["gender"], country = person[0]["country"])

@app.route("/registers", methods=["GET", "POST"])
@login_required
def registers():
    if request.method == "POST":
        id = db.execute("SELECT id FROM users WHERE passport = ?", session.get("passport"))[0]["id"]
        db.execute("DELETE FROM registers WHERE id_event = ? AND id_person = ?", request.form.get("event_id"), id)
        return redirect("/registers")
    else:
        id = db.execute("SELECT id FROM users WHERE passport = ?", session.get("passport"))[0]["id"]
        registers = db.execute("SELECT * FROM registers JOIN events ON registers.id_event = events.id WHERE id_person = ?", id)
        return render_template("registers.html", registers = registers)

@app.route("/event", methods=["GET"])
@login_required
def event():
    return render_template("event.html")
    
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        # Ensure title was submitted
        if not request.form.get("title"):
            return apology("must provide title", 403)

        # Ensure date was submitted
        elif not request.form.get("date"):
            return apology("must provide date", 403)

        # Ensure details was submitted
        elif not request.form.get("details"):
            return apology("must provide location", 403)

        # Ensure location was submitted
        elif not request.form.get("location"):
            return apology("must provide location", 403)

        db.execute("INSERT INTO events (title, location, details, date, price, people_number, another, hour, passport) VALUES (?,?,?,?,?,?,?,?,?)", 
        request.form.get("title"), request.form.get("location"), request.form.get("details"), request.form.get("date"),request.form.get("price"),
        request.form.get("limit"), request.form.get("another"), request.form.get("hour"),int(session.get("passport")))
        session["last_event"] = db.execute("SELECT id FROM events")[-1]["id"]
        return redirect("/create2")
    else:
        return render_template("create.html")

@app.route("/create2", methods=["GET", "POST"])
@login_required
def create2():
    if request.method == "POST":
        file = request.files['file']
        if file.filename == '':
            return apology("No image selected")
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("UPDATE events SET file = ? WHERE id = ?", filename, int(session.get("last_event")))

        return redirect("/")
    else:
        return render_template("create2.html")


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
        session["passport"] = rows[0]["passport"]
        session["first_name"] = rows[0]["first_name"]
        session["last_name"] = rows[0]["last_name"]
        session["image"] = 'Yes'
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
        return redirect('/register4')
    else:
        return render_template("register3.html")

@app.route("/register4", methods=["GET", "POST"])
def register4():
    if request.method == "POST":
        # Ensure bio was submitted
        if not request.form.get("bio"):
            return apology("must provide bio", 403)

        # Ensure phone gender was submitted
        elif not request.form.get("gender"):
            return apology("must provide gender", 403)

        elif not request.form.get("country"):
            return apology("must provide Country", 403)
        
        passport = session.get("passport")

        db.execute("UPDATE users SET bio = ?", request.form.get("bio"))
        db.execute("UPDATE users SET gender = ?", request.form.get("gender"))
        db.execute("UPDATE users SET country = ?", request.form.get("country"))
    
        return redirect('/')
    else:
        return render_template("register4.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)