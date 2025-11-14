from flask import Flask, render_template, request
import math

app = Flask(__name__)

user_ans = []

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
    return render_template("result.html")

@app.route("/guest", methods=["POST"])
def guest():
    required = ["nickname", "country", "greeting"]
    empty = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            empty.append(field)
    if len(empty) != 0:
        return render_template("guest_error.html", empty=empty)
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