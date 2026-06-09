from flask import (
    Flask,
    render_template,
    request,
    url_for,
    session,
    redirect,
)
from datetime import timedelta
import math
import csv
import os
import base64

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_KEY = (
    SUPABASE_SERVICE_ROLE_KEY
    or os.environ.get("SUPABASE_KEY")
    or SUPABASE_ANON_KEY
)

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    if SUPABASE_SERVICE_ROLE_KEY:
        app_logger_message = "Using SUPABASE_SERVICE_ROLE_KEY for Supabase client."
    else:
        app_logger_message = "Using anon Supabase key. Write operations may fail if RLS is enabled."
    print(app_logger_message)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "VerySecretKey"
)

app.permanent_session_lifetime = timedelta(days=30)

def login_user(encrypted_nickname):
    """Remember the logged-in user in a long-lived session cookie.

    The CSV files key everything on the *encrypted* nickname, so that is what
    we store for lookups; the decrypted name is kept only for display.
    """
    session.permanent = True
    session["user"] = encrypted_nickname
    session["display_name"] = decrypt(encrypted_nickname)

if os.environ.get("VERCEL"):
    DATA_DIR = "/tmp/.data"
else:
    DATA_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".data"
    )

LOGIN_CSV = os.path.join(DATA_DIR, "login.csv")
SCORES_CSV = os.path.join(DATA_DIR, "scores.csv")

LOGIN_HEADER = ["name", "nickname", "password"]
SCORES_HEADER = [
    "nickname",
    "subject",
    "grade",
    "class_grade",
    "std",
    "class_high_grade",
    "credits",
    "class_type",
    "r_score",
]


def ensure_data_files():
    """Create the data directory and CSV files (with headers) if missing.

    The .data/ folder is git-ignored and /tmp is wiped between cold starts,
    so the files must be (re)created on demand to avoid FileNotFoundError.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOGIN_CSV):
        with open(LOGIN_CSV, "w", newline="", encoding="utf-8") as csv_file:
            csv.writer(csv_file).writerow(LOGIN_HEADER)
    if not os.path.exists(SCORES_CSV):
        with open(SCORES_CSV, "w", newline="", encoding="utf-8") as csv_file:
            csv.writer(csv_file).writerow(SCORES_HEADER)


@app.before_request
def _prepare_data_files():
    ensure_data_files()


def globalScore(global_list):
    """
    Calculates the weighted global R-score for a student.
    Parameters:
        global_list (2D list): A list of [r_score, credit].
    Returns:
        global_score (float): Weighted average R-score rounded to 2 decimals.
    """
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


def encrypt_value(value):
    """Encrypt a value and wrap with enc: prefix."""
    if value is None or value == "":
        return value
    encrypted = encrypt(str(value))
    token = base64.urlsafe_b64encode(
        encrypted.encode("latin-1")
    ).decode("ascii")
    return f"enc:{token}"


def decrypt_value(value):
    """Decrypt a value that may have enc: prefix. Returns string."""
    if value is None or value == "":
        return value
    if isinstance(value, (int, float)):
        return str(value)

    value_str = str(value)
    if not value_str.startswith("enc:"):
        return value_str

    try:
        token = value_str.split("enc:", 1)[1]
        decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode(
            "latin-1"
        )
        return decrypt(decoded)
    except Exception:
        return value_str


def decrypt_numeric_value(value):
    """Decrypt a value and return as float. Returns None if invalid."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value)
    if value_str.startswith("enc:"):
        try:
            token = value_str.split("enc:", 1)[1]
            decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode(
                "latin-1"
            )
            return float(decrypt(decoded))
        except Exception:
            return None

    try:
        return float(value_str)
    except ValueError:
        return None


def decrypt_score_row(row):
    """Decrypt all fields in a score row."""
    row_copy = dict(row)
    row_copy["nickname"] = decrypt_value(row_copy.get("nickname"))
    row_copy["grade"] = decrypt_numeric_value(row_copy.get("grade"))
    row_copy["class_grade"] = decrypt_numeric_value(
        row_copy.get("class_grade")
    )
    row_copy["std"] = decrypt_numeric_value(row_copy.get("std"))
    row_copy["class_high_grade"] = decrypt_numeric_value(
        row_copy.get("class_high_grade")
    )
    row_copy["credits"] = decrypt_numeric_value(row_copy.get("credits"))
    row_copy["r_score"] = decrypt_numeric_value(row_copy.get("r_score"))
    return row_copy


def values_to_list(rows, username=None):
    """
    Converts score rows into a list containing ONLY the values and not its key.
    Parameters:
        rows: iterable of dict-like score rows
        username: username to filter their specific scores, defaults to none
    Returns:
        item_rows: (2D List) containing every value in the format
        ['nickname', 'subject', ...]
    """
    item_rows = []
    global_list = []
    found_user = False

    for row in rows:
        if row["nickname"].lower() == username.lower():
            decrypted_row = decrypt_score_row(row)
            found_user = True
            item_rows.append(
                [
                    decrypted_row["nickname"],
                    decrypted_row["subject"],
                    decrypted_row["grade"],
                    decrypted_row["class_grade"],
                    decrypted_row["std"],
                    decrypted_row["class_high_grade"],
                    decrypted_row["credits"],
                    decrypted_row["class_type"],
                    decrypted_row["r_score"],
                ]
            )
            if (
                decrypted_row["r_score"] is not None
                and decrypted_row["credits"] is not None
            ):
                global_list.append(
                    [
                        decrypted_row["r_score"],
                        decrypted_row["credits"],
                    ]
                )
    return item_rows, found_user, global_list


def supabase_enabled():
    return supabase is not None


def get_profile_by_nickname(encrypted_nickname):
    if not supabase_enabled():
        return None

    try:
        response = (
            supabase.table("profiles")
            .select("id, name, nickname, password")
            .eq("nickname", encrypted_nickname)
            .limit(1)
            .execute()
        )
        profile = response.data[0] if response.data else None
        if profile and profile.get("name"):
            profile["name"] = decrypt_value(profile.get("name"))
        return profile
    except Exception:
        return None


def verify_profile(encrypted_nickname, encrypted_password):
    profile = get_profile_by_nickname(encrypted_nickname)
    if profile and profile.get("password") == encrypted_password:
        return profile
    return None


def create_profile(name, encrypted_nickname, encrypted_password):
    try:
        response = (
            supabase.table("profiles")
            .insert([
                {
                    "name": name,
                    "nickname": encrypted_nickname,
                    "password": encrypted_password,
                }
            ])
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as exc:
        app.logger.exception(
            "Failed to create profile in Supabase. Verify SUPABASE_SERVICE_ROLE_KEY and row-level security policies."
        )
        return None


def get_scores_for_profile(profile_id, nickname=None):
    if not supabase_enabled():
        return []

    if profile_id is not None:
        try:
            response = (
                supabase.table("scores")
                .select("*, profiles(name)")
                .eq("profile_id", profile_id)
                .execute()
            )
            return response.data or []
        except Exception as exc:
            app.logger.warning(
                "get_scores_for_profile failed with profile_id fallback: %s",
                exc,
            )

    if nickname:
        try:
            response = (
                supabase.table("scores")
                .select("*")
                .eq("nickname", nickname)
                .execute()
            )
            return response.data or []
        except Exception as exc:
            app.logger.warning(
                "get_scores_for_profile failed with nickname fallback: %s",
                exc,
            )

    return []


def score_exists_for_profile(profile_id, subject, nickname=None):
    if not supabase_enabled():
        return False

    if profile_id is not None:
        try:
            response = (
                supabase.table("scores")
                .select("id")
                .eq("profile_id", profile_id)
                .eq("subject", subject)
                .limit(1)
                .execute()
            )
            return bool(response.data)
        except Exception as exc:
            app.logger.warning(
                "score_exists_for_profile failed with profile_id fallback: %s",
                exc,
            )

    if nickname:
        try:
            response = (
                supabase.table("scores")
                .select("id")
                .eq("nickname", nickname)
                .eq("subject", subject)
                .limit(1)
                .execute()
            )
            return bool(response.data)
        except Exception as exc:
            app.logger.warning(
                "score_exists_for_profile failed with nickname fallback: %s",
                exc,
            )

    return False


def insert_score(profile_id, nickname, subject, grade, class_grade, std, class_high_grade, credits, class_type, r_score):
    if not supabase_enabled():
        return None

    try:
        payload = {
            "nickname": nickname,
            "subject": subject,
            "grade": encrypt_value(grade),
            "class_grade": class_grade,
            "std": std,
            "class_high_grade": class_high_grade,
            "credits": credits,
            "class_type": class_type,
            "r_score": encrypt_value(r_score),
        }
        if profile_id is not None:
            payload["profile_id"] = profile_id

        response = (
            supabase.table("scores")
            .insert([payload])
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as exc:
        error_text = str(exc)
        app.logger.warning(
            "insert_score failed on Supabase insert: %s",
            error_text,
        )
        if "profile_id" in error_text or "Could not find the 'profile_id'" in error_text:
            try:
                response = (
                    supabase.table("scores")
                    .insert([
                        {
                            "nickname": nickname,
                            "subject": subject,
                            "grade": encrypt_value(grade),
                            "class_grade": class_grade,
                            "std": std,
                            "class_high_grade": class_high_grade,
                            "credits": credits,
                            "class_type": class_type,
                            "r_score": encrypt_value(r_score),
                        }
                    ])
                    .execute()
                )
                return response.data[0] if response.data else None
            except Exception as exc2:
                app.logger.exception(
                    "insert_score retry without profile_id failed.",
                )
        return None


def delete_last_score(profile_id=None, nickname=None):
    if not supabase_enabled():
        return False

    if profile_id is not None:
        try:
            response = (
                supabase.table("scores")
                .select("id")
                .eq("profile_id", profile_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if response.data:
                score_id = response.data[0].get("id")
                delete_response = (
                    supabase.table("scores")
                    .delete()
                    .eq("id", score_id)
                    .execute()
                )
                return bool(delete_response.data)
        except Exception as exc:
            app.logger.warning(
                "delete_last_score by profile_id failed: %s",
                exc,
            )

    if nickname:
        try:
            response = (
                supabase.table("scores")
                .select("id")
                .eq("nickname", nickname)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if not response.data:
                return False

            score_id = response.data[0].get("id")
            delete_response = (
                supabase.table("scores")
                .delete()
                .eq("id", score_id)
                .execute()
            )
            return bool(delete_response.data)
        except Exception as exc:
            app.logger.warning(
                "delete_last_score by nickname failed: %s",
                exc,
            )

    return False


def get_profile_id_by_nickname(encrypted_nickname):
    profile = get_profile_by_nickname(encrypted_nickname)
    return profile.get("id") if profile else None


def encrypt(text, shift=3):
    result = ""
    for i, char in enumerate(text):
        new_char = chr((ord(char) + shift + i) % 256)
        # We are storing the "encrypted" password and the username
        # by shifting its unicodes
        # Built in function to convert character to an unicode:
        # https://www.w3schools.com/python/ref_func_ord.asp
        # Built in function to convert unicode to a character:
        # https://www.w3schools.com/python/ref_func_chr.asp
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

@app.route("/future")
def future():
    return render_template("/future/future.html")

@app.route("/result_future", methods=["POST"])
def result_future():
    try:
        credit_done = float(request.form.get("credit_done"))
        credit_remaining = float(request.form.get("credit_remaining"))
        r_score = float(request.form.get("r_score"))
        user_grade = float(request.form.get("user_grade"))

        total = credit_done * user_grade
        desire_total = (credit_done + credit_remaining) * r_score
        r_score_needed = round((desire_total - total) / credit_remaining, 2)

        return render_template("/future/result_future.html", r_score_needed=r_score_needed, r_score=r_score)
    except (ValueError, TypeError, ZeroDivisionError):
        return render_template(
            "error.html",
            error_message="Something went wrong!",
            url=url_for("future"),
            submit_again="Submit Again",
        )

@app.route("/result_ad", methods=["POST"])
def result_ad():
    # calculates the probability of being admitted to a university course
    try:
        university = request.form.get("university")
        major = request.form.get("major")
        user_grade = float(request.form.get("user_grade"))
        cut_off = float(request.form.get("r_score"))

        Z = (user_grade - (cut_off - 0.025)) / 0.75
        cdf = (0.5 * (1 + math.erf(Z / math.sqrt(2)))) * 100
        # erf is an error function that is used in r-score calculations
        # source: https://docs.python.org/3/library/math.html
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
    # the r-score calculator and writing to csv file
    try:
        re_take = request.form.get("re_take")
        subject = request.form.get("subject").strip()
        grade = float(request.form.get("grade"))
        class_grade = float(request.form.get("class_grade"))
        std = float(request.form.get("class_std"))
        class_high_grade = float(request.form.get("class_high_grade"))
        subject_credit = float(request.form.get("credits"))
        class_type = request.form.get("science")
        # if the user is already logged in we reuse their session instead of
        # making them type their username and password again
        logged_in_user = session.get("user")
        if logged_in_user:
            nickname = logged_in_user
            password = None
        else:
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
        # verifies if username exists in login.csv / Supabase (skipped when
        # already authenticated through the session)
        username = None
        profile = None
        if logged_in_user:
            username = nickname
            if supabase_enabled():
                profile = get_profile_by_nickname(nickname)
        elif supabase_enabled():
            profile = verify_profile(nickname, password)
            if profile:
                username = nickname
        else:
            with open(LOGIN_CSV, mode="r", newline="") as csv_file:
                login = csv.DictReader(csv_file, delimiter=",")
                for row in login:
                    if (
                        row["nickname"].lower() == nickname.lower()
                        and row["password"] == password
                    ):
                        username = nickname
                        break

        # will return their r-score but it'll not be saved into the
        # scores.csv file
        if username is None:
            return render_template(
                "r_score/result_no_username.html",
                subject=subject,
                r_score=r_score,
            )

        # credentials are valid, so remember the user for next time
        login_user(username)

        # this block of code checks whether a user is trying to submit a
        # r-score for a subject they already submitted before
        if re_take != "yes":
            foundDuplicate = False
            if supabase_enabled() and profile:
                foundDuplicate = score_exists_for_profile(
                    profile.get("id"), subject, nickname
                )
            else:
                with open(SCORES_CSV, mode="r", newline="") as csv_file:
                    check_subject = csv.DictReader(csv_file)
                    for row in check_subject:
                        if (
                            row["nickname"].lower() == nickname.lower()
                            and row["subject"].lower() == subject.lower()
                        ):
                            foundDuplicate = True
                            break

            if foundDuplicate:
                password = decrypt(password) if password else ""
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

        if supabase_enabled() and profile:
            insert_score(
                profile.get("id"),
                nickname,
                subject,
                grade,
                class_grade,
                std,
                class_high_grade,
                subject_credit,
                class_type,
                r_score,
            )
            rows = get_scores_for_profile(profile.get("id"), username)
            rows, found_user, global_list = values_to_list(rows, username)
        else:
            with open(
                SCORES_CSV, mode="a", newline="", encoding="utf-8"
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(
                    [
                        nickname,
                        subject,
                        encrypt_value(grade),
                        encrypt_value(class_grade),
                        encrypt_value(std),
                        encrypt_value(class_high_grade),
                        encrypt_value(subject_credit),
                        class_type,
                        encrypt_value(r_score),
                    ]
                )
            with open(
                SCORES_CSV, mode="r", newline="", encoding="utf-8"
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                rows, found_user, global_list = values_to_list(
                    reader, username
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
            error_message="You have missing values! Please try again.",
            url=url_for("r_score"),
            submit_again="Submit Again",
        )


@app.route("/check_r_score")
def check_r_score():
    return render_template("/check_r_score/check_r_score.html")


@app.route("/my_r_score")
def my_r_score():
    # shows the logged-in user's R-Score without asking for credentials again
    encrypted_nickname = session.get("user")
    if not encrypted_nickname:
        return redirect(url_for("check_r_score"))

    if supabase_enabled():
        profile = get_profile_by_nickname(encrypted_nickname)
        if profile:
            rows = get_scores_for_profile(profile.get("id"), encrypted_nickname)
            rows, found_user, global_list = values_to_list(
                rows, encrypted_nickname
            )
        else:
            rows, found_user, global_list = [], False, []
    else:
        with open(
            SCORES_CSV, mode="r", newline="", encoding="utf-8"
        ) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            rows, found_user, global_list = values_to_list(
                reader, encrypted_nickname
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
    return render_template(
        "r_score/result.html",
        display_message="These are your R-scores",
        past_score=rows,
        global_score=global_score,
        username=session.get("display_name"),
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login():
    # logs an existing user in from the sign up page
    try:
        nickname = encrypt(request.form.get("nickname", "").strip())
        password = encrypt(request.form.get("password", ""))
    except AttributeError:
        nickname = ""
        password = ""

    if supabase_enabled():
        profile = verify_profile(nickname, password)
        if profile:
            login_user(nickname)
            return redirect(url_for("my_r_score"))
    else:
        with open(
            LOGIN_CSV, mode="r", newline="", encoding="utf-8"
        ) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            for row in reader:
                if (
                    row["nickname"].lower() == nickname.lower()
                    and row["password"] == password
                ):
                    login_user(nickname)
                    return redirect(url_for("my_r_score"))

    error_message = (
        "Your account doesn't exist, or your login information is "
        "incorrect. Sign up below to create an account."
    )
    return render_template(
        "error.html",
        error_message=error_message,
        url=url_for("signup"),
        submit_again="Try Again",
    )


@app.route("/your_r_score", methods=["POST"])
def your_r_score():
    # skips submitting an r-score to see the r-score table with the overall
    # r-score from username and password
    try:
        nickname = encrypt(request.form.get("nickname"))
        password = encrypt(request.form.get("password"))
        username = None
        profile = None

        if supabase_enabled():
            profile = verify_profile(nickname, password)
            if profile:
                username = nickname
        else:
            # verifies username AND password
            with open(
                LOGIN_CSV, mode="r", newline="", encoding="utf-8"
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

        # credentials are valid, so remember the user for next time
        login_user(username)

        if supabase_enabled() and profile:
            rows = get_scores_for_profile(profile.get("id"), username)
            rows, found_user, global_list = values_to_list(
                rows, username
            )
        else:
            # goes to the helper function values_to_list to return a list
            # of data to show to the user in a table
            with open(
                SCORES_CSV, mode="r", newline="", encoding="utf-8"
            ) as csv_file:
                reader = csv.DictReader(csv_file, delimiter=",")
                rows, found_user, global_list = values_to_list(
                    reader, username
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
    # signup to r-score calculator to save r-score data
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

    if supabase_enabled():
        if get_profile_by_nickname(nickname):
            nickname = decrypt(nickname)
            return render_template(
                "signup/account_exists.html",
                nickname=nickname,
            )

        encrypted_name = encrypt_value(name)
        profile = create_profile(encrypted_name, nickname, password)
        if not profile:
            return render_template(
                "error.html",
                error_message="Unable to create account at this time.",
                url=url_for("signup"),
                submit_again="Try Again",
            )

        login_user(nickname)
        nickname = decrypt(nickname)
        return render_template("signup/welcome.html", username=nickname)

    csv_path = LOGIN_CSV

    # verifies if account already exists
    with open(csv_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["nickname"].lower() == nickname.lower():
                nickname = decrypt(nickname)
                return render_template(
                    "signup/account_exists.html",
                    nickname=nickname,
                )
    # write to login.csv the new account
    encrypted_name = encrypt_value(name)
    with open(csv_path, "a", newline="", encoding="utf-8") as csv_file:
        data = csv.writer(csv_file, delimiter=",")
        data.writerow([encrypted_name, nickname, password])

    # new accounts are logged in automatically
    login_user(nickname)
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
    # allows user to remember their password if they have a valid username
    # and name
    try:
        username = encrypt(request.form.get("nickname"))
        name = request.form.get("name")

        if supabase_enabled():
            profile = get_profile_by_nickname(username)
            if profile and profile.get("name", "").lower() == name.lower():
                password = profile.get("password")
                return render_template(
                    "signup/password_result.html",
                    password=decrypt(password),
                )
        else:
            with open(
                LOGIN_CSV, mode="r", newline="", encoding="utf-8"
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    stored_name = decrypt_value(row["name"])
                    if (
                        row["nickname"].lower() == username.lower()
                        and stored_name.lower() == name.lower()
                    ):
                        password = row["password"]
                        return render_template(
                            "signup/password_result.html",
                            password=decrypt(password),
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
    # button to remove LATEST r-score
    user_name = encrypt(request.form.get("username").strip())
    if supabase_enabled():
        profile_id = get_profile_id_by_nickname(user_name)
        delete_last_score(profile_id, user_name)
        rows = get_scores_for_profile(profile_id, user_name)
    else:
        fieldnames = []
        user_rows = []
        # gets all the the current data from scores.csv
        with open(SCORES_CSV, mode="r",
                  newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            fieldnames = reader.fieldnames
            rows = list(reader)
        # appends all specific r-score rows of the user from the main list 'rows'
        # to user_rows
        if rows:
            user_row_indices = []
            for i, row in enumerate(rows):
                if row["nickname"].lower() == user_name.lower():
                    user_rows.append(row)
                    user_row_indices.append(i)

            if user_row_indices:
                # removing the last submitted r-score from the main list 'rows'
                # using the index to ensure we remove the correct item
                last_index = user_row_indices[-1]
                rows.pop(last_index)
        # writing the updated list into the a new csv file
        with open(SCORES_CSV, mode="w",
                  newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # converting it to values to be displayed to the user
    item_row, found_user, global_list = values_to_list(rows,
                                                       user_name,
                                                       )
    
    if global_list:
        global_score = globalScore(global_list)
    else:
        global_score = "0"

    display_message = "Score removed successfully!"
    user_name = decrypt(user_name)
    return render_template(
        "r_score/result.html",
        display_message=display_message,
        past_score=item_row,
        global_score=global_score,
        username=user_name,
    )
