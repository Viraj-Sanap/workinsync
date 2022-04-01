import sqlite3
from flask import redirect, render_template, request, session, flash
from functools import wraps


def create_table():
    connection = sqlite3.connect('workinsync.db')
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS 'users'('username' TEXT NOT NULL UNIQUE, 'hash'"
                   " TEXT NOT NULL,	slots INTEGER, PRIMARY KEY('username'))")

    cursor.execute("CREATE TABLE IF NOT EXISTS 'meeting'('m_id' integer NOT NULL, 'title' TEXT NOT NULL,"
                   "'username' TEXT NOT NULL, 'date' DATE NOT NULL, 'fromtime' DATE NOT NULL, 'endtime' DATE NOT NULL,"
                   " 'room' TEXT NOT NULL, PRIMARY KEY('m_id' AUTOINCREMENT) "
                   "FOREIGN KEY(username) references users(username) on delete cascade on update cascade)")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology_slot():
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    message = "Slot is already Booked!"
    return render_template("check.html", slot=message, message2=session["user_id"])


def exist_slot():
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    message = "Slot is available!"
    return render_template("check.html", slote=message, message2=session["user_id"])


def apology_exists():
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    message = "Username already exists!"
    return render_template("register.html", message3=message)


def apology_match():
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    message = "Password and Confirm Password do not match."
    return render_template("register.html", message3=message)


def apology_login():
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    message = "Username does not Exist!"
    return render_template("login.html", message=message)


def apology_login2():
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    message = "Password is incorrect!"
    return render_template("login.html", message=message)

def apology_none():
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    nomeet = "No Booking History!"
    return render_template("history.html", nomeet=nomeet, message2=session["user_id"])

