from flask import Flask, render_template, request
import math

app = Flask(__name__)

user_ans = []
SUGGESTIONS = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/r_score")
def r_score():
    return render_template("r_score.html")

@app.route("/admissions")
def admissions():
    return render_template("admissions.html")

@app.route("/result_ad", methods=["POST"])
def result_ad():
    try:
        university = request.form.get("university")
        major = request.form.get("major")
        user_grade = float(request.form.get("user_grade"))
        cut_off = float(request.form.get("r_score"))
        Z = (user_grade - (cut_off - 0.025)) / 0.75
        cdf = (0.5 * (1 + math.erf(Z / math.sqrt(2))))*100
        chance = round(cdf, 2)
    
        return render_template("result_ad.html", 
                                chance=chance, 
                                university=university, 
                                major=major, 
                                user_grade=user_grade, 
                                cut_off=cut_off)
    
    except:
        return render_template("error_ad.html")
    
@app.route("/explanation")
def explanation():
    return render_template("explanation.html")

@app.route("/result", methods=["POST"])
def result():
    try:
        subject = float(request.form.get("subject"))
        grade = float(request.form.get("grade"))
        class_grade = float(request.form.get("class_grade")) + 0.45
        class_high_grade = float(request.form.get("class_high_grade"))
        std = float(request.form.get("class_std"))
        IDGZ = (request.form.get("science"))
        if IDGZ == "No":
            IDGZ = 1.19
        elif IDGZ == "Yes":
            IDGZ = 0.75
        else:
            return render_template("error.html")
        ISGZ = (class_high_grade-73.64)/14.12
        r_score = round((((grade - class_grade)/std)*IDGZ+ISGZ+5)*5, 2)

        return render_template("result.html", r_score=r_score, subject=subject)
    
    except:
        return render_template("error.html")

@app.route("/guest", methods=["POST"])
def guest():
    required = ["nickname", "country", "greeting"]
    missing_field = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            missing_field.append(field)
    if len(missing_field) != 0:
        return render_template("guest_error.html", missing_field=missing_field)
    else:
        global nickname
        nickname = request.form.get("nickname")
        country = request.form.get("country")
        greeting = request.form.get("greeting")
        return render_template("guest.html",
                                nickname=nickname,
                                country=country,
                                greeting=greeting)
    
@app.route("/guestbook")
def guestbook():
    user_ans.append(nickname)
    print(user_ans)
    return render_template("guestbook.html", user_ans=user_ans)

@app.route("/suggestion", methods=["POST"])
def suggestion():
    return render_template("suggestion.html")
    
@app.route("/suggestion_result", methods=["POST"])
def suggestion_result():
    global suggestion
    required_fields = ["name", "email", "suggestion"]

    name = request.form.get("name")
    email = request.form.get("email")
    suggestion = request.form.get("suggestion")

    accepted_email = "@dawsoncollege.qc.ca"

    for field in required_fields:
        if not request.form.get(field):
            return render_template("suggestion_error.html")

    if accepted_email not in email:
        return render_template("suggestion_error_email.html")
    return render_template("suggestion_result.html", name=name, suggestion=suggestion)

@app.route("/suggestion_leaderboard")
def suggestion_leaderboard():
    SUGGESTIONS.append(suggestion)
    return render_template("suggestion_leaderboard.html", SUGGESTIONS=SUGGESTIONS)
