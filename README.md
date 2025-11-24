Fitness Health Tracker
A wellness web app to log meals and workouts, automatically calculate calories, track weekly progress, and estimate eco impact from walking. Built with a Python backend, HTML templates, and a MySQL database.

Features
Automatic fruit calories: enter a fruit name and get accurate calorie estimates based on per‑100g nutrition values and sensible default portions.
Smart exercise tracking: calculates calories burned using standard MET formulas and your profile data such as weight, height, and age.
Weekly insights: shows total and average calories, calorie balance, workout minutes, distance walked, sessions, streaks, badges, and helpful coaching tips.
Environmental impact: estimates distance walked and CO₂ saved for walking activities.
Secure authentication: register and login with hashed passwords and session‑based access.
Data browsing: view recent entries for users and food logs.
Simple REST API: fetch summary stats for use by external clients.
Architecture
Backend: a Flask application exposing routes for landing, authentication, dashboard, data logging, and a lightweight API.
Presentation: Jinja2 templates render HTML pages for the landing, login, registration, dashboard, and entries views.
Static assets: a CSS stylesheet served via Flask’s static file support to style the UI.
Database: MySQL stores users, food logs, exercise logs, and environment logs. SQL scripts provide schema and optional trigger fixes.
Data flow: user actions create logs (food and exercise) which drive dashboard calculations and insights; walking activities also update environmental impact.
Directory Structure
Fitness Health Tracker/
├─ finess_health_tracker_backend/
│  ├─ app.py
│  ├─ config.py
│  ├─ static/
│  │  └─ style.css
│  ├─ templates/
│  │  ├─ index.html
│  │  ├─ login.html
│  │  ├─ register.html
│  │  ├─ dashboard.html
│  │  └─ entries.html
│  ├─ README.md
│  ├─ fix_database_triggers.py
│  └─ requirements.txt
├─ requirement.txt
├─ fitness_tracker_db.sql
├─ fix_triggers.sql
├─ fix_user_summary_error.sql
├─ Database_Flowchart*.mmd
└─ ER_Diagram.mmd
Setup
Prerequisites:

Python 3.13+
MySQL Server
Install dependencies:

python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirement.txt
Configure database:

Update MySQL credentials in the backend configuration file.
Create the database and import the schema: mysql -u <user> -p <password> < fitness_tracker_db.sql.
If triggers cause errors, apply the provided SQL fixes or run the helper script.
Run server:

.\.venv\Scripts\python finess_health_tracker_backend\app.py
Open http://127.0.0.1:5000/
Usage
Landing: visit / to see the introductory page.
Register/Login: create an account at /register then sign in at /login.
Dashboard: view weekly reports, tips, badges at /dashboard.
Log food: submit the form to add a meal; fruit names auto‑calculate calories.
Log exercise: submit activity and duration; calories burned are computed and walking logs CO₂ saved.
Entries: browse users and food logs at /entries.
API: GET /api/summary/<user_id> returns JSON summary data.
Example API call:

curl http://127.0.0.1:5000/api/summary/1
Notes
Ensure the static files configuration points to the correct static folder so the CSS loads.
Change the secret key before any production deployment.
Use the root requirement.txt for dependency installation.
MySQL trigger behavior can vary by environment; the repository includes optional fixes.
License
Personal/educational use. Adapt as needed for production deployments.

