from flask import Flask, render_template, request, url_for
import math
import csv

app = Flask(__name__)


def globalScore(global_list):
    if not global_list:
        return 0

    weighted_sum = 0
    total_weight = 0

    for score, weight in global_list:
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return 0

    global_score = round(weighted_sum / total_weight, 2)
    return global_score


def values_to_list(rows, username=None, verified=True):
    item_rows = []
    global_list = []
    found_user = False

    for row in rows:
        if verified or row["nickname"] == username.lower():
            found_user = True
            item_rows.append(
                [
                    row["nickname"],
                    row["subject"],
                    row["grade"],
                    row["class_grade"],
                    row["std"],
                    row["class_high_grade"],
                    row["credits"],
                    row["class_type"],
                    row["r_score"],
                ]
            )
            if row["r_score"] and row["credits"]:
                global_list.append(
                    [float(row["r_score"]), float(row["credits"])]
                )

    return item_rows, found_user, global_list


def encrypt(text, shift=3):
    result = ""
    for i, char in enumerate(text):
        new_char = chr((ord(char) + shift + i) % 256)
        result += new_char
    return result[::-1]


def decrypt(text, shift=3):
    text = text[::-1]
    result = ""
    for i, char in enumerate(text):
        new_char = chr((ord(char) - shift - i) % 256)
        result += new_char
    return result


user_ans = []
user_suggestions = []
nickname = None
suggestion = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/r_score")
def r_score():
    return render_template("/r_score/r_score.html")


@app.route("/admissions")
def admissions():
    return render_template("/admissions/admissions.html")


@app.route("/result_ad", methods=["POST"])
def result_ad():
    try:
        university = request.form.get("university")
        major = request.form.get("major")
        user_grade = float(request.form.get("user_grade"))
        cut_off = float(request.form.get("r_score"))

        Z = (user_grade - (cut_off - 0.025)) / 0.75
        cdf = (0.5 * (1 + math.erf(Z / math.sqrt(2)))) * 100
        chance = round(cdf, 2)

        if not university or not major:
            raise ValueError("Missing university or major")

        return render_template(
            "/admissions/result_ad.html",
            chance=chance,
            university=university,
            major=major,
            user_grade=user_grade,
            cut_off=cut_off,
        )

    except (ValueError, TypeError, AttributeError):
        return render_template(
            "error.html",
            error_message="You have missing values!",
            url=url_for("admissions"),
            submit_again="Submit Again",
        )


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
        nickname = encrypt(request.form.get("nickname").strip())
        password = encrypt(request.form.get("password"))

        if std == 0:
            error_message = (
                "the standard deviation can not be 0"
            )
            return render_template(
                "error.html",
                error_message=error_message,
                url=url_for("r_score"),
                submit_again="Submit Again",
            )

        if class_type == "No":
            IDGZ = 1.19
        elif class_type == "Yes":
            IDGZ = 0.75
        else:
            error_message = (
                "You didn't answer the question: "
                "Is this a science course? "
                "Please try again."
            )
            return render_template(
                "error.html",
                error_message=error_message,
                url=url_for("r_score"),
                submit_again="Submit Again",
            )

        ISGZ = (class_high_grade - 73.64) / 14.12
        r_score = round((
            ((grade - class_grade + 0.45) / std) * IDGZ + ISGZ + 5
        ) * 5, 2)

        username = None
        with open(".data/login.csv", mode="r", newline="") as csv_file:
            login = csv.DictReader(csv_file, delimiter=",")
            for row in login:
                if (
                    row["nickname"].lower() == nickname.lower()
                    and row["password"] == password
                ):
                    username = nickname
                    break

        if username is None:
            return render_template(
                "r_score/result_no_username.html",
                subject=subject,
                r_score=r_score
            )

        if re_take != "yes":
            foundDuplicate = False
            with open(".data/scores.csv", mode="r", newline="") as csv_file:
                check_subject = csv.DictReader(csv_file)
                for row in check_subject:
                    if (
                        row["nickname"].lower() == nickname.lower()
                        and row["subject"].lower() == subject.lower()
                    ):
                        foundDuplicate = True
                        break

            if foundDuplicate:
                password = decrypt(password)
                nickname = decrypt(nickname)
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
                    "password": password,
                }
                return render_template(
                    "r_score/subject_exist.html", score_data=score_data
                )

        with open(
            ".data/scores.csv", mode="a", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    nickname,
                    subject,
                    grade,
                    class_grade,
                    std,
                    class_high_grade,
                    subject_credit,
                    class_type,
                    r_score,
                ]
            )

        with open(
            ".data/scores.csv", mode="r", newline="", encoding="utf-8"
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            rows, found_user, global_list = values_to_list(
                reader, username, verified=False
            )

        global_score = globalScore(global_list)
        display_message = (
            f"Your latest calculated r-score for " f"{subject} is {r_score}"
        )
        nickname = decrypt(nickname)
        return render_template(
            "r_score/result.html",
            display_message=display_message,
            past_score=rows,
            global_score=global_score,
            username=nickname,
        )

    except (ValueError, TypeError, AttributeError):
        return render_template(
            "error.html",
            error_message="You have missing values! " "Please try again.",
            url=url_for("r_score"),
            submit_again="Submit Again",
        )


@app.route("/check_r_score")
def check_r_score():
    return render_template("/check_r_score/check_r_score.html")


@app.route("/your_r_score", methods=["POST"])
def your_r_score():
    try:
        nickname = encrypt(request.form.get("nickname"))
        password = encrypt(request.form.get("password"))
        username = None
        with open(
            ".data/login.csv", mode="r", newline="", encoding="utf-8"
        ) as csv_file:
            login = csv.DictReader(csv_file, delimiter=",")
            for row in login:
                if (
                    row["nickname"].lower() == nickname.lower()
                    and row["password"] == password
                ):
                    username = nickname
                    break

            if not username:
                error_message = (
                    "Your account doesn't exist, or "
                    "your login information is incorrect. Go to the "
                    "Sign Up page to create an account."
                )
                return render_template(
                    "error.html",
                    error_message=error_message,
                    url=url_for("check_r_score"),
                    submit_again="Try Again",
                )

        with open(
            ".data/scores.csv", mode="r", newline="", encoding="utf-8"
        ) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            rows, found_user, global_list = values_to_list(
                reader, username, verified=False
            )

        if not found_user:
            error_message = "You do not have any calculated R-Score!"
            return render_template(
                "error.html",
                error_message=error_message,
                url=url_for("r_score"),
                submit_again="Calculate your R-Score",
            )

        global_score = globalScore(global_list)

        display_message = "These are your R-scores"
        nickname = decrypt(nickname)
        return render_template(
            "r_score/result.html",
            display_message=display_message,
            past_score=rows,
            global_score=global_score,
            username=nickname,
        )

    except (ValueError, TypeError, AttributeError, ZeroDivisionError):
        return render_template(
            "error.html",
            error_message="Something went wrong. " "Please try again.",
            url=url_for("check_r_score"),
            submit_again="Try Again",
        )


@app.route("/signup")
def signup():
    return render_template("/signup/signup.html")


@app.route("/signup_result", methods=["POST"])
def signup_result():
    name = request.form.get("name")
    nickname = encrypt(request.form.get("nickname").strip())
    password = encrypt(request.form.get("password"))
    required = ["name", "nickname", "password"]
    missing_field = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            missing_field.append(field)
    if missing_field:
        error_message = "You are missing: " + " & ".join(missing_field) + "."
        return render_template(
            "error.html",
            error_message=error_message,
            url=url_for("signup"),
            submit_again="Try Again",
        )

    csv_path = ".data/login.csv"

    with open(csv_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["nickname"].lower() == nickname.lower():
                nickname = decrypt(nickname)
                return render_template(
                    "signup/account_exists.html",
                    nickname=nickname
                )

    with open(csv_path, "a", newline="", encoding="utf-8") as csv_file:
        data = csv.writer(csv_file, delimiter=",")
        data.writerow([name, nickname, password])

    nickname = decrypt(nickname)
    return render_template("signup/welcome.html", username=nickname)


@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


@app.route("/guest", methods=["POST"])
def guest():
    required = ["nickname", "country", "greeting"]
    missing_field = []
    for field in required:
        if not request.form.get(field).replace(" ", ""):
            missing_field.append(field)
    if len(missing_field) != 0:
        error_message = "You are missing: " + " & ".join(missing_field) + "."
        return render_template(
            "error.html",
            error_message=error_message,
            url=url_for("admissions"),
            submit_again="Try Again",
        )
    else:
        global nickname
        nickname = request.form.get("nickname")
        country = request.form.get("country")
        greeting = request.form.get("greeting")
        return render_template(
            "admissions/guest.html",
            nickname=nickname,
            country=country,
            greeting=greeting,
        )


@app.route("/guestbook")
def guestbook():
    user_ans.append(nickname)
    return render_template("admissions/guestbook.html", user_ans=user_ans)


@app.route("/suggestion_result", methods=["POST"])
def suggestion_result():
    global suggestion
    required_fields = ["name", "email", "suggestion"]

    name = request.form.get("name")
    email = request.form.get("email")
    suggestion = request.form.get("suggestion")

    if not email.endswith("@dawsoncollege.qc.ca"):
        error_message = (
            "Your email didn't end with @dawsoncollege.qc.ca. "
            "You're not a Dawson student! Please try again."
        )
        return render_template(
            "error.html",
            error_message=error_message,
            url=url_for("r_score"),
            submit_again="Try Again",
        )

    for field in required_fields:
        if not request.form.get(field):
            error_message = "You have missing answers. " "Please try again."
            return render_template(
                "error.html",
                error_message=error_message,
                url=url_for("r_score"),
                submit_again="Try Again",
            )

    return render_template(
        "r_score/suggestion_result.html", name=name, suggestion=suggestion
    )


@app.route("/suggestion_leaderboard")
def suggestion_leaderboard():
    user_suggestions.append(suggestion)
    return render_template(
        "r_score/suggestion_leaderboard.html",
        user_suggestions=user_suggestions
    )


@app.route("/password")
def password():
    return render_template("signup/password.html")


@app.route("/password_result", methods=["POST"])
def password_result():
    try:
        username = encrypt(request.form.get("nickname"))
        name = request.form.get("name")

        with open(
            ".data/login.csv", mode="r", newline="", encoding="utf-8"
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if (
                    row["nickname"].lower() == username.lower()
                    and row["name"].lower() == name.lower()
                ):
                    password = row["password"]
                    return render_template(
                        "signup/password_result.html",
                        password=decrypt(password)
                    )

        error_message = "Your account does not exist."
        return render_template(
            "error.html",
            error_message=error_message,
            url=url_for("password"),
            submit_again="Submit Again",
        )

    except (ValueError, TypeError, AttributeError):
        error_message = "Something went wrong. Please try again."
        return render_template(
            "error.html",
            error_message=error_message,
            url=url_for("password"),
            submit_again="Submit Again",
        )


@app.route("/remove_last_score", methods=["POST"])
def remove_last_score():
    user_name = encrypt(request.form.get("username").strip())
    fieldnames = []
    user_rows = []

    with open(".data/scores.csv", mode="r",
              newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",")
        fieldnames = reader.fieldnames
        rows = list(reader)

    if rows:
        for row in rows:
            if row["nickname"].lower() == user_name.lower():
                user_rows.append(row)

        if user_rows:
            try:
                item_remove = user_rows[-1]
                rows.remove(item_remove)
            except ValueError:
                pass

    with open(".data/scores.csv", mode="w",
              newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    item_row, found_user, global_list = values_to_list(rows,
                                                       user_name,
                                                       verified=False)

    if not found_user:
        error_message = "You do not have any calculated R-Score!"
        return render_template(
            "error.html",
            error_message=error_message,
            url=url_for("r_score"),
            submit_again="Calculate your R-Score",
        )

    if global_list:
        global_score = globalScore(global_list)
    else:
        global_score = "0"

    display_message = "Updated!"
    user_name = decrypt(user_name)
    return render_template(
        "r_score/result.html",
        display_message=display_message,
        past_score=item_row,
        global_score=global_score,
        username=user_name,
    )
