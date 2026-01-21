from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Job, Application, SavedJob   # <<< ADDED SavedJob
import requests, os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs("uploads", exist_ok=True)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        # 🔎 Check if username already exists
        existing = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if existing:
            return render_template(
                "register.html",
                error="Username already exists"
            )

        # ✅ Create new user
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role=request.form["role"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")



# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    error=None
    if request.method=="POST":
        user=User.query.filter_by(username=request.form["username"]).first()
        if user and user.active and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))
        error="Invalid credentials or account blocked."
    return render_template("login.html", error=error)


# ---------- LOGOUT ----------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------- POST JOB ----------
@app.route("/post_job", methods=["GET","POST"])
@login_required
def post_job():
    if current_user.role != "employer":
        return redirect(url_for("index"))

    if request.method == "POST":
        job = Job(
            title=request.form["title"],
            company=request.form["company"],
            location=request.form["location"],
            salary=request.form["salary"],
            category=request.form["category"],
            description=request.form["description"],
            employer_id=current_user.id,
            contact_email=request.form["contact_email"],
            contact_phone=request.form["contact_phone"]
        )
        db.session.add(job)
        db.session.commit()
        return redirect(url_for("employer_jobs"))

    return render_template("post_job.html")


# ---------- EDIT JOB ----------
@app.route("/edit_job/<int:job_id>", methods=["GET","POST"])
@login_required
def edit_job(job_id):
    job=Job.query.get_or_404(job_id)
    if current_user.role!="employer" or job.employer_id!=current_user.id:
        return redirect(url_for("index"))

    if request.method=="POST":
        job.title=request.form["title"]
        job.company=request.form["company"]
        job.location=request.form["location"]
        job.salary=request.form["salary"]
        job.category=request.form["category"]
        job.description=request.form["description"]
        db.session.commit()
        return redirect(url_for("employer_jobs"))
    return render_template("edit_job.html", job=job)


# ---------- EMPLOYER JOB LIST ----------
@app.route("/employer_jobs")
@login_required
def employer_jobs():
    jobs=Job.query.filter_by(employer_id=current_user.id).all()
    return render_template("employer_jobs.html", jobs=jobs)


# ---------- DELETE JOB ----------
@app.route("/delete_job/<int:job_id>")
@login_required
def delete_job(job_id):
    job=Job.query.get_or_404(job_id)
    if current_user.role=="employer" and job.employer_id!=current_user.id:
        return redirect(url_for("index"))

    Application.query.filter_by(job_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()

    return redirect(url_for("admin" if current_user.role=="admin" else "employer_jobs"))


# ---------- APPLY (WITH CANDIDATE DETAILS + RESUME) ----------
@app.route("/apply/<int:job_id>", methods=["GET","POST"])
@login_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)

    if current_user.role != "jobseeker":
        return redirect(url_for("jobs"))

    if request.method == "POST":
        existing = Application.query.filter_by(
            user_id=current_user.id,
            job_id=job_id
        ).first()
        if existing:
            return redirect(url_for("my_applications"))
        file = request.files["resume"]
        filename = secure_filename(f"{current_user.id}_{job_id}_{file.filename}")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        app_obj = Application(
            user_id=current_user.id,
            job_id=job_id,
            resume=filename,
            full_name=request.form["full_name"],
            email=request.form["email"],
            phone=request.form["phone"],
            message=request.form["message"]
        )

        db.session.add(app_obj)
        db.session.commit()

        return render_template("application_submitted.html", job=job)

    return render_template("apply_internal.html", job=job)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------- VIEW APPLICANTS ----------
@app.route("/applicants/<int:job_id>")
@login_required
def applicants(job_id):
    job=Job.query.get_or_404(job_id)
    if job.employer_id!=current_user.id:
        return redirect(url_for("index"))
    apps=Application.query.filter_by(job_id=job_id).all()
    return render_template("applicants.html", apps=apps, job=job)


# ---------- UPDATE APPLICATION STATUS ----------
@app.route("/update_status/<int:app_id>/<status>")
@login_required
def update_status(app_id,status):
    app_obj=Application.query.get_or_404(app_id)
    job=Job.query.get(app_obj.job_id)
    if job.employer_id!=current_user.id:
        return redirect(url_for("index"))
    app_obj.status=status
    db.session.commit()
    return redirect(url_for("applicants", job_id=job.id))



# ====================================================
#           JOB APIS
# ====================================================
def remotive_jobs(keyword):
    try:
        d=requests.get("https://remotive.com/api/remote-jobs",timeout=5).json()
    except:
        return []
    jobs=[]
    for j in d.get("jobs",[]):
        if keyword and keyword not in j["title"].lower(): continue
        jobs.append({
            "title": j["title"],"company": j["company_name"],
            "location": j["candidate_required_location"],
            "category":"Remote","source":"Remotive",
            "apply_type":"external","url": j["url"]
        })
    return jobs


def arbeitnow_jobs(keyword):
    try:
        d=requests.get("https://www.arbeitnow.com/api/job-board-api",timeout=5).json()
    except:
        return []
    jobs=[]
    for j in d.get("data",[]):
        if keyword and keyword not in j["title"].lower(): continue
        jobs.append({
            "title": j["title"],"company": j["company_name"],
            "location": j["location"],"category":"General",
            "source":"Arbeitnow","apply_type":"external","url": j["url"]
        })
    return jobs


# ---------- JOB SEARCH ----------
@app.route("/jobs")
def jobs():
    keyword=request.args.get("search","").lower()
    location=request.args.get("location","").lower()
    category=request.args.get("category","").lower()

    results=[]

    for job in Job.query.all():
        if (keyword in f"{job.title} {job.company}".lower()
            and location in job.location.lower()
            and category in job.category.lower()):
            results.append({
                "title":job.title,"company":job.company,
                "location":job.location,"category":job.category,
                "source":"Internal","apply_type":"internal","job_id":job.id
            })

    results.extend(remotive_jobs(keyword))
    results.extend(arbeitnow_jobs(keyword))

    return render_template("jobs.html", jobs=results)



# ====================================================
#        JOB SEEKER FEATURES
# ====================================================

# ---------- SAVE JOB ----------
@app.route("/save_job/<int:job_id>")
@login_required
def save_job(job_id):
    if current_user.role != "jobseeker":
        return redirect(url_for("jobs"))

    exists = SavedJob.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()

    if not exists:
        db.session.add(SavedJob(user_id=current_user.id, job_id=job_id))
        db.session.commit()

    return redirect(url_for("jobs"))


# ---------- VIEW SAVED JOBS ----------
@app.route("/saved_jobs")
@login_required
def saved_jobs():
    saved = SavedJob.query.filter_by(user_id=current_user.id).all()
    job_ids = [s.job_id for s in saved]
    jobs = Job.query.filter(Job.id.in_(job_ids)).all() if job_ids else []
    return render_template("saved_jobs.html", jobs=jobs)

@app.route("/unsave_job/<int:job_id>")
@login_required
def unsave_job(job_id):
    if current_user.role != "jobseeker":
        return redirect(url_for("jobs"))

    SavedJob.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).delete()

    db.session.commit()

    return redirect(url_for("saved_jobs"))


# ---------- VIEW MY APPLICATIONS ----------
@app.route("/my_applications")
@login_required
def my_applications():
    apps = Application.query.filter_by(user_id=current_user.id).all()
    jobs = {j.id: j for j in Job.query.all()}
    return render_template("my_applications.html", apps=apps, jobs=jobs)



# ---------- ADMIN ----------
@app.route("/admin")
@login_required
def admin():
    # 🔐 Restrict access to admin only
    if current_user.role != "admin":
        return redirect(url_for("index"))

    return render_template(
        "admin.html",
        users=User.query.all(),
        jobs=Job.query.all(),
        applications=Application.query.all()
    )


@app.route("/toggle_user/<int:user_id>")
@login_required
def toggle_user(user_id):
    user=User.query.get_or_404(user_id)
    user.active=not user.active
    db.session.commit()
    return redirect(url_for("admin"))


@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
