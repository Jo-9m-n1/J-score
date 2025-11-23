from flask import Flask, render_template, request
import math
import csv

app = Flask(__name__)

user_ans = []
user_suggestions = []

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

@app.route("/result", methods=["POST"])
def result():
    try:
        subject = request.form.get("subject")
        grade = float(request.form.get("grade"))
        class_grade = float(request.form.get("class_grade"))
        std = float(request.form.get("class_std")) 
        class_high_grade = float(request.form.get("class_high_grade"))
        subject_credit = float(request.form.get("credits"))
        class_type = request.form.get("science")
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        
        if class_type == "No":
            IDGZ = 1.19
        elif class_type == "Yes":
            IDGZ = 0.75
        else:
            return render_template("error.html")
        ISGZ = (class_high_grade-73.64)/14.12
        r_score = round((((grade - class_grade + 0.45)/std)*IDGZ+ISGZ+5)*5, 2)

        username = None
        with open('.data/login.csv', mode='r', newline='') as csv_file:
            login = csv.DictReader(csv_file, delimiter=',')
            for row in login:
                if row['nickname'].lower() == nickname.lower() and row['password'] == password:
                    username = nickname
                    break
        
        if username == None:
            return render_template("error_username.html", subject=subject, r_score=r_score)
        
        with open('.data/scores.csv', 'a', newline='') as csv_file:
            data = csv.writer(csv_file, delimiter=',')
            data.writerow([nickname,
                           subject,
                           grade,
                           class_grade,
                           std,
                           class_high_grade,
                           subject_credit,
                           class_type,
                           r_score])

        rows = []
        global_list = []
        weigthed_sum = 0
        total_weight = 0
        with open('.data/scores.csv', mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',') 
            for row in reader:
                if row['nickname'] == username:
                    rows.append([
                        row['nickname'],
                        row['subject'],
                        row['grade'],
                        row['class_grade'],
                        row['std'],
                        row['class_high_grade'],
                        row['credits'],
                        row['class_type'],
                        row['r_score']
                    ])
                    global_list.append([float(row['r_score']), float(row['credits'])])

        for item in global_list:
            score, weight = item
            weigthed_sum += score * weight
            total_weight += weight

        global_score = round(weigthed_sum/total_weight, 2)

        return render_template("result.html", 
                               subject=subject, 
                               grade=grade, 
                               class_grade=class_grade, 
                               std=std, 
                               class_high_grade=class_high_grade, 
                               credits=subject_credit, 
                               science_class=class_type, 
                               r_score=r_score,
                               past_score=rows,
                               global_score=global_score)
    
    except:
        return render_template("error.html")
    
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_result", methods=["POST"])
def signup_result():
    nickname = request.form.get("username")
    password = request.form.get("password")
    required = ["username", "password"]
    missing = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            missing.append(field)
    if len(missing) != 0:
        return render_template("missing.html", missing=missing)
    
    csv_path = '.data/login.csv'

    with open(csv_path, mode='r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["nickname"].lower() == nickname.lower():
                return render_template("account_exists.html", nickname=nickname)
            
    with open(csv_path, 'a', newline='') as csv_file:
        data = csv.writer(csv_file, delimiter=',')
        data.writerow([nickname, password])
    return render_template("index.html")

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

    if not email.endswith("@dawsoncollege.qc.ca"):
        return render_template("suggestion_error.html", error_message="Your email didn't end with @dawsoncollege.qc.ca. You're not a Dawson student! Please try again:")
    for field in required_fields:
        if not request.form.get(field):
            return render_template("suggestion_error.html", error_message="You have missing answers. Please try again:")

    return render_template("suggestion_result.html", name=name, suggestion=suggestion)

@app.route("/suggestion_leaderboard")
def suggestion_leaderboard():
    user_suggestions.append(suggestion)
    return render_template("suggestion_leaderboard.html", user_suggestions=user_suggestions)
