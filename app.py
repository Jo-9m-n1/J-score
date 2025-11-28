from flask import Flask, render_template, request, url_for
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

@app.route("/result_ad", methods=["POST", "GET"]) # TAKE IT OUT!
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
        error_message = "You have missing values!"
        submit_again = "Submit Again"
        return render_template("error.html", error_message=error_message, url=url_for('admissions'), submit_again=submit_again)

@app.route("/result", methods=["POST"])
def result():
    try:
        re_take = request.form.get("re_take")
        subject = request.form.get("subject").strip()
        grade = float(request.form.get("grade"))
        class_grade = float(request.form.get("class_grade"))
        std = float(request.form.get("class_std")) 
        class_high_grade = float(request.form.get("class_high_grade"))
        subject_credit = float(request.form.get("credits"))
        class_type = request.form.get("science")
        nickname = request.form.get("nickname").strip()
        password = request.form.get("password")
        
        if class_type == "No":
            IDGZ = 1.19
        elif class_type == "Yes":
            IDGZ = 0.75
        else:
            return render_template("error.html", error_message="You didn't answer the question: Is this a science course? Please try again.", url=url_for('r_score'), submit_again="Submit Again")
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
        
        if re_take != "yes":
            foundDuplicate = False
            with open('.data/scores.csv', mode='r', newline='') as csv_file:
                check_subject = csv.DictReader(csv_file)   
                for row in check_subject:
                    if row['nickname'].lower() == nickname.lower() and row['subject'].lower() == subject.lower():    
                        foundDuplicate = True
                        break

            if foundDuplicate:
                score_data = {
                    "nickname": nickname,
                    "subject": subject,
                    "grade": grade,
                    "class_grade": class_grade,
                    "class_std": std,
                    "class_high_grade": class_high_grade,
                    "credits": subject_credit,
                    "science": class_type,
                    "r_score": r_score,
                    "password": password
                }
                return render_template("subject_exist.html", score_data=score_data)

        with open('.data/scores.csv', mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                nickname,
                subject,
                grade,
                class_grade,
                std,
                class_high_grade,
                subject_credit,
                class_type,
                r_score
            ])

        with open('.data/scores.csv', mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            rows, found_user, global_list = values_to_list(reader, username, verified=False)   

        if not found_user:
            return render_template("missing_score.html")        
        
        global_score = globalScore(global_list)
        display_message = (f"Your latest calculated r-score for {subject} is {r_score}")

        return render_template("result.html", display_message=display_message, past_score=rows, global_score=global_score, username=nickname)
    
    except:
        return render_template("error.html", error_message="You have missing values! Please try again.", url=url_for('r_score'), submit_again="Submit Again")

@app.route("/check_r_score")
def check_r_score():
    return render_template("check_r_score.html")

@app.route("/your_r_score", methods=["POST"])
def your_r_score():
    try:
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        username = None
        with open('.data/login.csv', mode='r', newline='') as csv_file:
            login = csv.DictReader(csv_file, delimiter=',')
            for row in login:
                if row['nickname'].lower() == nickname.lower() and row['password'] == password:
                    username = nickname
                    break
            
            if username == None:
                return render_template("account_not_exist.html")
            
        with open('.data/scores.csv', mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            rows, found_user, global_list = values_to_list(reader, username, verified=False) 

        if not found_user:
            return render_template("missing_score.html")
        
        global_score = globalScore(global_list)

        display_message = "e"
        print(nickname)
        return render_template("result.html", display_message=display_message, past_score=rows, global_score=global_score, username=nickname)
    
    except:
        render_template("error_check.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_result", methods=["POST"])
def signup_result():
    name = request.form.get("name")
    nickname = request.form.get("nickname").strip()
    password = request.form.get("password")
    required = ["name", "username", "password"]
    missing_field = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            missing_field.append(field)
    if len(missing_field) != 0:
        return render_template("missing_error.html", missing_field=missing_field)
    
    csv_path = '.data/login.csv'

    with open(csv_path, mode='r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["nickname"].lower() == nickname.lower():
                return render_template("account_exists.html", nickname=nickname)
            
    with open(csv_path, 'a', newline='') as csv_file:
        data = csv.writer(csv_file, delimiter=',')
        data.writerow([name, nickname, password])
    return render_template("welcome.html", username=nickname)

@app.route("/welcome")
def welcome():
    render_template("welcome.html")

@app.route("/guest", methods=["POST"])
def guest():
    required = ["nickname", "country", "greeting"]
    missing_field = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            missing_field.append(field)
    if len(missing_field) != 0:
        return render_template("missing_error_sign.html", missing_field=missing_field)
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
        return render_template("error.html", error_message="Your email didn't end with @dawsoncollege.qc.ca. You're not a Dawson student! Please try again.")
    for field in required_fields:
        if not request.form.get(field):
            return render_template("error.html", error_message="You have missing answers. Please try again.")

    return render_template("suggestion_result.html", name=name, suggestion=suggestion)

@app.route("/suggestion_leaderboard")
def suggestion_leaderboard():
    user_suggestions.append(suggestion)
    return render_template("suggestion_leaderboard.html", user_suggestions=user_suggestions)

@app.route("/password")
def password():
    return render_template("password.html")

@app.route("/password_result", methods=["POST"])
def password_result():
    try:
        username = request.form.get("nickname")
        name = request.form.get("name")

        with open('.data/login.csv', mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["nickname"].lower() == username.lower() and row["name"].lower() == name.lower():
                    password = row["password"]
                    return render_template("password_result.html", password=password)
        return render_template("account_not_exist.html")
    except:
        return render_template("error_pass.html")
            
@app.route("/remove_last_score", methods=["POST"])
def remove_last_score():
    user_name = request.form.get("username").strip()
    fieldnames = []
    user_rows = []

    with open('.data/scores.csv', mode='r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        fieldnames = reader.fieldnames
        rows = list(reader)

    if rows:
        for row in rows:
            if row['nickname'].lower() == user_name.lower():
                user_rows.append(row)
        for row in rows:
            if user_rows[-1] == row:
                rows.remove(row)

    with open('.data/scores.csv', mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    

    item_row, found_user, global_list = values_to_list(rows, user_name, verified=False) 

    if not found_user:
        return render_template("missing_score.html")    
        
    if global_list:
        global_score = globalScore(global_list)
    else:
        global_score = "0"

    display_message = "Updated!"  

    return render_template("result.html", display_message=display_message, past_score=item_row, global_score=global_score, username=user_name)

def globalScore(global_list):
    weighted_sum = 0
    total_weight = 0
    for item in global_list:
        score, weight = item
        weighted_sum += score * weight
        total_weight += weight
    global_score = round(weighted_sum/total_weight, 2)
    return global_score

def values_to_list(rows, username=None, verified=True):
    item_rows = []
    global_list = []
    found_user = False

    for row in rows:
        if verified or row['nickname'] == username.lower():
            found_user = True
            item_rows.append([
                row['nickname'],
                row['subject'],
                row['grade'],
                row['class_grade'],
                row['std'],
                row['class_high_grade'],
                row['credits'],
                row['class_type'],
                row['r_score'],
            ])
            if row['r_score'] and row['credits']:
                global_list.append([float(row['r_score']), float(row['credits'])])

    return item_rows, found_user, global_list
