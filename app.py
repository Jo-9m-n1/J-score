from flask import Flask, render_template, request
import math

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/r_score")
def r_score():
    return render_template("r_score.html")

@app.route("/admissions")
def admissions():
    return render_template("admissions.html")

@app.route("/admissions/result_ad", methods=["POST"])
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