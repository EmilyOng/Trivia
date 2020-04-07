from flask import Flask, redirect, request, url_for, render_template, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient

from user import User
from dotenv import load_dotenv

import sqlite3
import json
import os
import random
import requests

project_folder = os.path.expanduser("~/Trivia")
load_dotenv(os.path.join(project_folder, ".env"))

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL")

connection = sqlite3.connect("Trivia.db")
cursor = connection.cursor()
ADMINS = cursor.execute("SELECT Email FROM Admin").fetchall()

def unique_digits (size, type="G"):
    digits = []
    for i in range (size):
        digits.append(str(random.randint(0,9)))
    return type + "".join(digits)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provided_cfg ():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@login_manager.user_loader
def load_user (user_id):
    return User.get(user_id)

@app.route("/privateTrivia", methods=["GET", "POST"])
def privateTrivia ():
    if request.form and "privateTrivia" not in request.form:return redirect(url_for("index"))
    session["privateTrivia"] = request.form["privateTrivia"]
    session["game_type"] = "private"
    return redirect(url_for("play"))

@app.route("/globalTrivia", methods=["GET", "POST"])
def globalTrivia ():
    if request.form and "globalTrivia" not in request.form:return redirect(url_for("index"))
    session["game_type"] = "global"
    connection = sqlite3.connect("Trivia.db")
    cursor = connection.cursor()
    cursor.execute("SELECT QuestionID, QuestionType, QuestionText from Question WHERE QuestionGroup = 'Global'")
    result = cursor.fetchall()
    questions = {}
    answers = {}
    for res in result:
        questionID = res[0]
        cursor.execute("SELECT Option1, Option2, Option3, Answer from Option WHERE QuestionID = ?", (questionID,))
        options = cursor.fetchone()
        questions[questionID] = {}
        questions[questionID]["QuestionType"] = res[1]
        questions[questionID]["questionText"] = res[2]
        given_options = [options[0], options[1], options[2]]
        random.shuffle(given_options)
        questions[questionID]["options"] = given_options
        answer_index = int(options[-1]) - 1
        answers[questionID] = options[answer_index]
        # questions[questionID]["answer"] = options[answer_index]

    connection.close()
    session["questions"] = questions
    session["answers"] = answers
    return redirect(url_for("play"))

@app.route("/addQuestion", methods=["GET", "POST"])
def addQuestion():
    if (session and "is_admin" in session) and not session["is_admin"]:return redirect(url_for("index"))
    if request.form:
        if "submitGlobalQuestion" in request.form:
            session["submitted_global"] = True
            # QUESTION: Should use a non-relational database instead?
            questionText = request.form["questionText"]
            options = ["" for i in range (3)]
            index = 0
            fields = list(request.form.keys())
            check_unique_options = set()
            for field in fields:
                if "optionText" in field:
                    options[index] = request.form[field]
                    check_unique_options.add(request.form[field])
                    index += 1

            if len(check_unique_options) != index:
                session["error_msg"] = "The options must be unique."
            else:
                answer = request.form["answer"]
                questionID = unique_digits(4, "G")
                connection = sqlite3.connect("Trivia.db")
                cursor = connection.cursor()
                while True:
                    cursor.execute("SELECT * FROM Question WHERE questionID=?", (questionID,))
                    result = cursor.fetchone()
                    if result!=None:questionID = unique_digits(4, "G")
                    else:break
                cursor.execute("INSERT INTO Question (QuestionID, QuestionGroup, QuestionType, QuestionText) VALUES (?, ?, ?, ?)",
                                (questionID, "Global", "MCQ", questionText))
                connection.commit()
                cursor.execute("INSERT INTO Option (QuestionID, Option1, Option2, Option3, Answer) VALUES (?, ?, ?, ?, ?)",
                                (questionID, options[0], options[1], options[2], answer))
                connection.commit()
                connection.close()
    return redirect(url_for("admin"))


@app.route("/submitAnswers", methods=["GET", "POST"])
def submitAnswers () :
    if not current_user.is_authenticated:return redirect(url_for("index"))
    questions = session["questions"]
    result = {}
    connection = sqlite3.connect("Trivia.db")
    cursor = connection.cursor()
    for response in request.form:
        questionID = response
        given_answer = request.form[questionID]
        options = cursor.execute("SELECT Option1, Option2, Option3, Answer FROM Option WHERE QuestionID = ?", (questionID, )).fetchone()
        answer_index = int(options[-1]) - 1
        correct_answer = options[answer_index]
        result[questionID] = {}
        result[questionID]["given"] = given_answer
        result[questionID]["correct"] = correct_answer
        attemptNum = cursor.execute("SELECT AttemptNum FROM Score WHERE UserID = ? AND QuestionID = ?", (current_user.id_, questionID)).fetchall()
        if attemptNum == None or len(attemptNum) == 0:
            updatedAttemptNum = 1
        else:
            # print(attemptNum)
            updatedAttemptNum = attemptNum[-1][0] + 1
        # print(current_user.id_,questionID,updatedAttemptNum)
        cursor.execute("INSERT INTO Score (UserID, QuestionID, AttemptNum, GivenAnswer) VALUES (?, ?, ?, ?)", (current_user.id_, questionID, updatedAttemptNum, given_answer))
        connection.commit()
    connection.close()
    session["result"] = result
    print(result)
    return redirect(url_for("play"))

@app.route("/admin")
def admin ():
    if (session and "is_admin" in session) and not session["is_admin"]:return redirect(url_for("index"))
    submitted = False
    error_msg = None
    if session:
        if "error_msg" in session:
            error_msg = session["error_msg"]
            session.pop("error_msg")
        elif "submitted_global" in session:
            submitted = True
            session.pop("submitted_global")
    return render_template("admin.html", submitted=submitted, error_msg=error_msg)

@app.route("/play")
def play ():
    if not current_user.is_authenticated:return redirect(url_for("index"))
    if session and "game_type" in session:
        if "global" in session["game_type"]:
            msg = None
            questions = None
            answers = None
            result = None
            if "questions" in session:questions = session["questions"]
            else:msg = "There are no available questions."
            if "answers" in session:answers = session["answers"]
            if "result" in session:
                result = session["result"]
                session.pop("result")
                print(result)
            return render_template("play.html", questions=json.dumps(questions), answers=json.dumps(answers),
                                    result=result, msg=msg)
        elif "private" in session["game_type"]:
            pass
        else:return redirect(url_for("index"))
    else:return redirect(url_for("index"))
    return render_template("play.html")

@app.route("/")
def index ():
    session["is_admin"] = False
    if current_user.is_authenticated:
        for admin in ADMINS:
            if current_user.email == admin[0]:session["is_admin"] = True
        user_info = {"id": current_user.id_,
                    "name": current_user.name,
                    "email": current_user.email,
                    "profile_pic": current_user.profile_pic}
        return render_template("start_game.html", user_info=user_info, is_admin=session["is_admin"])
    return render_template("index.html")

@app.route("/login")
def login ():
    google_provided_cfg = get_google_provided_cfg()
    authorization_endpoint = google_provided_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri = request.base_url + "/callback",
        scope = ["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route ("/login/callback")
def callback ():
    code = request.args.get("code")
    google_provided_cfg = get_google_provided_cfg()
    token_endpoint = google_provided_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response = request.url,
        redirect_url = request.base_url,
        code = code
    )
    token_response = requests.post(
        token_url,
        headers = headers,
        data = body,
        auth = (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provided_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        userinfo = userinfo_response.json()
        unique_id = userinfo["sub"]
        user_email = userinfo["email"]
        picture = userinfo["picture"]
        username = userinfo["name"]
        user = User(id_=unique_id, name=username, email=user_email, profile_pic=picture)
        if not User.get(unique_id):
            User.create(unique_id, username, user_email, picture)
        login_user(user)
        return redirect(url_for("index"))
    else:
        return render_template("index.html", msg="User email not available or verified by Google.")

@app.route("/logout")
@login_required
def logout ():
    logout_user()
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context="adhoc", debug=True)
