import os
import time
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functions import login_required, create_table, apology_match, apology_exists, apology_login, \
    apology_login2, apology_slot, exist_slot, apology_none

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

current = os.path.dirname(os.path.abspath(__file__))


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
@login_required
def main():
    return render_template("login.html")


@app.route("/index", methods=["GET"])
@login_required
def index():
    connection = sqlite3.connect("workinsync.db")
    connection.row_factory = sqlite3.Row
    db = connection.cursor()

    read = "SELECT * FROM users where username = ?"
    db.execute(read, [session["user_id"]], )
    user_check = db.fetchall()
    print(user_check)
    print(session["user_id"])

    readm = "SELECT * FROM meeting WHERE username = ? AND date > Date()"
    db.execute(readm, [session["user_id"]], )
    meeting = db.fetchall()
    print(meeting)
    print(session["user_id"])

    return render_template("index.html", user=user_check, meeting=meeting, message2=session["user_id"])


@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    if request.method == "POST":

        date = request.form.get("date")
        fromtime = request.form.get("fromtime")
        endtime = request.form.get("endtime")
        room = request.form.get("room")

        print(date)

        connection = sqlite3.connect("workinsync.db")
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        read = "SELECT * FROM meeting WHERE username = ? AND room = ? AND date = ? AND " \
               "(fromtime >= ? AND fromtime <= ?);"
        db.execute(read, [session["user_id"], room, date, fromtime, endtime],)
        rows = db.fetchone()
        print(rows)

        print("check")
        print(date)
        print(fromtime)

        # Ensure the username doesn't exists
        if rows is not None:
            return apology_slot()

        else:
            return exist_slot()

    else:
        return render_template("check.html", message2=session["user_id"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        password1 = request.form.get("password1")

        connection = sqlite3.connect("workinsync.db")
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        read = "SELECT * FROM users WHERE username = ?"
        db.execute(read, [username])
        rows = db.fetchone()
        print(rows)

        print("check")

        # Ensure the username doesn't exists
        if rows is not None:
            return apology_exists()

        # Ensure passwords match
        elif not password == password1:
            return apology_match()

        else:
            print("check")

            hash1 = generate_password_hash(
                password, method="pbkdf2:sha256", salt_length=8
            )

            print("check")
            # Insert the new user

            insert = "INSERT INTO users (username, hash, slots) VALUES (?, ?, 5) "
            db.execute(insert, (username, hash1,))
            connection.commit()

            # Redirect user to home page
            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    create_table()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username

        connection = sqlite3.connect("workinsync.db")
        connection.row_factory = sqlite3.Row
        db = connection.cursor()
        read = "SELECT * FROM users WHERE username = ?"
        db.execute(read, [username])
        user_one = db.fetchone()
        print(user_one)
        print(password)
        # Ensure username exists and password is correct

        if user_one is None:
            print("no user")
            return apology_login()

        if not check_password_hash(user_one[1], password):
            print("no pass")
            return apology_login2()

        # Remember which user has logged in
        session["user_id"] = user_one[0]

        read = "SELECT * FROM users where username = ?"
        db.execute(read, [session["user_id"]], )
        user_check = db.fetchall()
        print(user_check)
        print(session["user_id"])

        readm = "SELECT * FROM meeting WHERE username = ? AND date > Date()"
        db.execute(readm, [session["user_id"]], )
        meeting = db.fetchall()
        print(meeting)
        print(session["user_id"])

        return render_template("index.html", user=user_check, meeting=meeting, message2=session["user_id"])

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("login.html")


@app.route("/history", methods=["GET"])
@login_required
def history():
    connection = sqlite3.connect("workinsync.db")
    connection.row_factory = sqlite3.Row
    db = connection.cursor()

    read = "SELECT * FROM meeting WHERE username = ?"
    db.execute(read, [session["user_id"]], )
    meeting = db.fetchall()
    print(meeting)
    print(session["user_id"])

    if meeting is None:
        return apology_none()

    else:
        return render_template("history.html", meeting=meeting, message2=session["user_id"])


@app.route("/book", methods=["GET", "POST"])
@login_required
def book():

    if request.method == "POST":
        title = request.form.get("title")
        date = request.form.get("date")
        fromtime = request.form.get("fromtime")
        endtime = request.form.get("endtime")
        room = request.form.get("room")

        connection = sqlite3.connect("workinsync.db")
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        check = "SELECT TIME(?) - TIME(?)"

        db.execute(check, (endtime, fromtime))
        recheck = db.fetchall()
        connection.commit()
        print("recheck")
        ans = 0
        for row in recheck:
            ans = row[0]

        print(ans)

        read = "SELECT slots FROM users where username = ?"
        db.execute(read, (session["user_id"],))
        slots = db.fetchall()
        connection.commit()
        print("slots")
        comp = 0
        for row in slots:
            comp = row[0]

        print(comp)
        print(ans)

        if comp >= ans:
            insert = "INSERT INTO meeting (title, date, fromtime, endtime, room, username) VALUES (?, ?, ?, ?, ?, ?)"
            db.execute(insert, (title, date, fromtime,
                                endtime, room, session["user_id"],))
            connection.commit()

            update = "UPDATE users SET slots = slots - ? where username = ?"
            db.execute(update, (ans, session["user_id"],))
            connection.commit()

            success = "Meeting Room was booked successfully!"

            return render_template("book.html", message2=session["user_id"], success=success)

        else:
            slot = "You do not have enough slots!"

            return render_template("book.html", message2=session["user_id"], slot=slot)

    else:
        return render_template("book.html", message2=session["user_id"])


@app.route("/cancel", methods=["GET", "POST"])
@login_required
def cancel():

    if request.method == "POST":

        del_id = request.form.get("del_id")

        connection = sqlite3.connect("workinsync.db")
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        check = "SELECT TIME(endtime) - TIME(fromtime) from meeting where m_id=?"
        db.execute(check, del_id,)
        recheck = db.fetchall()
        connection.commit()
        print("recheck")
        ans = 0
        for row in recheck:
            ans = row[0]

        update = "UPDATE users SET slots = slots + ? where username = ?"
        db.execute(update, (ans, session["user_id"],))
        connection.commit()

        delete = "DELETE FROM meeting WHERE m_id = ?"
        db.execute(delete, [del_id])
        connection.commit()

        print("deleted")
        print(del_id)

        read = "SELECT * FROM meeting WHERE username = ? AND date >= DATE(CURRENT_DATE) AND fromtime > " \
               "TIME(CURRENT_TIME) ORDER BY date, fromtime"
        db.execute(read, [session["user_id"]], )
        meeting = db.fetchall()
        print(meeting)
        print(session["user_id"])

        success = "Deleted Successfully!"

        return render_template("cancel.html", meeting=meeting, message2=session["user_id"], success=success)

    else:
        connection = sqlite3.connect("workinsync.db")
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        read = "SELECT * FROM meeting WHERE username = ? AND date >= DATE(CURRENT_DATE) AND fromtime > " \
               "TIME(CURRENT_TIME) ORDER BY date, fromtime"
        db.execute(read, [session["user_id"]],)
        meeting = db.fetchall()
        print(meeting)
        print(session["user_id"])

        return render_template("cancel.html", meeting=meeting, message2=session["user_id"])


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if request.method == "POST":

        p_admin = request.form.get("p_admin")

        if p_admin == "admin":
            connection = sqlite3.connect("workinsync.db")
            connection.row_factory = sqlite3.Row
            db = connection.cursor()

            read = "SELECT * FROM users"
            db.execute(read,)
            meeting = db.fetchall()
            print(meeting)
            print(session["user_id"])

            return render_template("admin.html", meeting=meeting, message2=session["user_id"])

        else:
            wrong = "Incorrect Password"
            return render_template("admin.html", wrong=wrong, message2=session["user_id"])

    else:
        return render_template("admin.html", message2=session["user_id"])
