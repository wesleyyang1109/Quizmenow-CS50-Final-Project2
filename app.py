import os
# export API_KEY=pk_cecf84bddcf94c8c9713436ab37e70e6
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///quiz.db")




@app.route("/")
@login_required
def index():
    return render_template("index.html")




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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        elif len(db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))) != 0:
            return apology("username has been used", 400)

        username = request.form.get("username")

        hash = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        return render_template("login.html")
    else:
        return render_template("register.html")

    # User reached route via GET (as by clicking a link or via redirect)



@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":

        user_id = session["user_id"]
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            return apology("passwords do not match")

        hash = generate_password_hash(request.form.get("password"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, user_id)

        return redirect("/")

    else:
        return render_template("change_password.html")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        quiz_name = request.form.get("quiz_name")
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
        date_time = datetime.datetime.now()

        if not quiz_name:
            return apology("must provide quiz name", 400)
        

        db.execute("INSERT INTO quizes (username, user_id, quiz_name, datetime) VALUES(?, ?, ?, ?)", username, user_id, quiz_name, date_time)
        count = int(request.form.get("total"))

        #id = db.execute("SELECT quiz_id FROM quizes WHERE user_id = ? AND quiz_name = ?", user_id, quiz_name)[0]["quiz_id"]
        id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

        for x in range(count):
            question_name = request.form.get(f"question_name{x+1}")
            answer_a = request.form.get(f"Q{x+1}A")
            answer_b = request.form.get(f"Q{x+1}B")
            answer_c = request.form.get(f"Q{x+1}C")
            answer_d = request.form.get(f"Q{x+1}D")
            correct = request.form.get(f"q{x+1}")

            if not answer_a or not answer_b or not answer_c or not answer_d or not question_name:
                db.execute("DELETE FROM questions WHERE id = ?", id);
                db.execute("DELETE FROM quizes WHERE quiz_id = ?", id);
                return apology("must provide question and answers", 400)
            db.execute("INSERT INTO questions (id, question, answer_a, answer_b, answer_c, answer_d, correct) VALUES(?, ?, ?, ?, ?, ?, ?)", id, question_name, answer_a, answer_b, answer_c, answer_d, correct)

        return redirect("/")
        
    else:
        return render_template("editor.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        search = request.form.get("search")
        searched = "%" + search + "%"
        rows = db.execute("SELECT * FROM quizes WHERE quiz_name LIKE ?", searched)
        return render_template("searched.html", rows=rows, search=search)
    else:

        return render_template("search.html")        


@app.route("/quizmenow", methods=["GET", "POST"])
@login_required
def quizmenow():
    if request.method == "POST":
        count = request.form.get("count")
        quiz_id = request.form.get("quiz_id")
        rows = db.execute("SELECT * FROM questions WHERE id = ?", quiz_id)
        counter = 0
        list = []
        quiz_name = db.execute("SELECT quiz_name FROM quizes WHERE quiz_id = ?", quiz_id)[0]['quiz_name']
           
        for row in rows:
            counter += 1
            picked = request.form.get(f"q{ counter }")
            if row['correct'] == picked:
                x = dict(question_count = counter, correctmarker = 1, chosen = picked)
                list.append(x)               
            else:
                x = dict(question_count = counter, correctmarker = 0, chosen = picked)
                list.append(x)

        for i in range(counter):
            rows[i].update(list[i]) 

        return render_template("results.html", rows=rows, quiz_name=quiz_name) 
    else:
        quiz_id = request.args.get("quizid")
        rows = db.execute("SELECT * FROM questions WHERE id = ?", quiz_id)
        quiz_name = db.execute("SELECT quiz_name FROM quizes WHERE quiz_id = ?", quiz_id)[0]['quiz_name']
        return render_template("quizmenow.html", rows=rows, quiz_id=quiz_id, quiz_name=quiz_name)

        
@app.route("/edit", methods=["GET"])
@login_required
def edit():
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM quizes WHERE user_id = ?", user_id)
    return render_template("editchoose.html", rows=rows) 


@app.route("/editor2", methods=["GET", "POST"])
@login_required
def editor2():
    if request.method == "POST":
        quiz_name = request.form.get("quiz_name")
        user_id = session["user_id"]
        count = int(request.form.get("total"))
        date_time = datetime.datetime.now()

        quiz_id = request.form.get("quiz_id") #db.execute("SELECT quiz_id FROM quizes WHERE user_id = ? AND quiz_name = ?", user_id, quiz_name)[0]["quiz_id"]

        if not quiz_name:
            return apology("must provide quiz name", 400)

        db.execute("UPDATE quizes SET quiz_name = ?, datetime = ? WHERE user_id = ? AND quiz_id = ?", quiz_name, date_time, user_id, quiz_id)

        db.execute("DELETE FROM questions WHERE id = ?", quiz_id);

        for x in range(count):
            question_name = request.form.get(f"question_name{x+1}")
            answer_a = request.form.get(f"Q{x+1}A")
            answer_b = request.form.get(f"Q{x+1}B")
            answer_c = request.form.get(f"Q{x+1}C")
            answer_d = request.form.get(f"Q{x+1}D")
            correct = request.form.get(f"q{x+1}")

            if not answer_a or not answer_b or not answer_c or not answer_d or not question_name:
                db.execute("DELETE FROM questions WHERE id = ?", quiz_id);
                db.execute("DELETE FROM quizes WHERE quiz_id = ?", quiz_id);
                return apology("must provide question and answers", 400)
            else:
                db.execute("INSERT INTO questions (id, question, answer_a, answer_b, answer_c, answer_d, correct) VALUES(?, ?, ?, ?, ?, ?, ?)", quiz_id, question_name, answer_a, answer_b, answer_c, answer_d, correct)


        return redirect("/")

    else:
        quiz_id = request.args.get("quizid")
        rows = db.execute("SELECT * FROM questions WHERE id = ?", quiz_id)
        count = len(rows)
        quiz_name = db.execute("SELECT quiz_name FROM quizes WHERE quiz_id = ?", quiz_id)[0]['quiz_name']
        return render_template("editor2.html", rows=rows, count=count, quiz_name=quiz_name, quiz_id=quiz_id)

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        quiz_id = request.form.get("quizid")
        db.execute("DELETE FROM questions WHERE id = ?", quiz_id);
        db.execute("DELETE FROM quizes WHERE quiz_id = ?", quiz_id);
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM quizes WHERE user_id = ?", user_id)
        return render_template("editchoose.html", rows=rows)
    else:
        return render_template("index.html")

@app.route("/guide")
@login_required
def guide():
    return render_template("guide.html")
#def errorhandler(e):
    #"""Handle error"""
    #if not isinstance(e, HTTPException):
    #    e = InternalServerError()
    #return apology(e.name, e.code)


# Listen for errors
#for code in default_exceptions:
#   app.errorhandler(code)(errorhandle)
