Job Portal Web Application

A full-stack job portal built with Flask (Python) that allows:

✔ Job Seekers to search, apply, and track applications
✔ Employers to post jobs and manage applicants
✔ Admin to manage users and system data
✔ Integration with multiple external Job APIs
✔ Resume upload and Applicant Tracking

This project simulates real-world platforms like LinkedIn / Indeed / Naukri.

🚀 Features
👤 Job Seekers

Register and Login

Browse jobs from:

Internal postings

External Job APIs (Remotive, ArbeitNow)

Apply for jobs with resume upload

Save jobs and apply later

Remove saved jobs

View all jobs they have applied for

Track application status (Pending / Accepted / Rejected)

👨‍💼 Employers

Create job postings

Edit and delete posted jobs

View list of applicants per job

Download uploaded resumes

Accept / Reject applications

🛡 Admin

View all users

Block / unblock users

Delete users

Monitor jobs and applications

🌍 APIs Used

External jobs are fetched from:

Remotive Jobs API

ArbeitNow API

Providing real-time job results beyond portal entries.

🏗 Tech Stack

Backend: Flask (Python)
Database: SQLite (SQLAlchemy ORM)
Frontend: HTML, CSS, Bootstrap
Auth: Flask-Login
API Integration: REST APIs via Requests

📂 Project Structure
project/
│── app.py
│── models.py
│── requirements.txt
│── README.md
│── database.db (or job_portal.sqlite3)
│── uploads/
│── templates/
│   ├── base.html
│   ├── index.html
│   ├── jobs.html
│   ├── post_job.html
│   ├── employer_jobs.html
│   ├── applicants.html
│   ├── apply_internal.html
│   ├── application_submitted.html
│   ├── saved_jobs.html
│   ├── my_applications.html
│   ├── login.html
│   └── register.html

▶️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/job-portal.git
cd job-portal

2️⃣ Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   (Windows)
source venv/bin/activate (Mac/Linux)

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the app
python app.py


Then open in your browser:

http://127.0.0.1:5000

🔐 User Roles Summary
Role	Capabilities
Job Seeker	Search, Apply, Save jobs, Track status
Employer	Post, Edit, Delete jobs, View applicants
Admin	Manage users & system data
📌 Future Enhancements

Email notifications to employer/applicant

Resume screening automation (AI matching)

Job recommender system

Deployment on Render/Heroku

Dashboard analytics

🤝 Contributing

Pull requests and suggestions are welcome — this project is intended for learning and academic use.

📄 License

This project is open-source and free to use for educational purposes.