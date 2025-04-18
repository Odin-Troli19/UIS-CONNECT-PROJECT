# UIS-Connect – Social Media Platform for Students

This is a simple social media platform database project built for the DAT220 course. It allows students at the University of Stavanger (UIS) to connect, share posts, and interact with each other.

##  Group 36
- Sture Troli  


##  Features
- User profiles with major and interests
- Posting, liking, and commenting on posts
- Friend connections between users
- Web app built with Flask and SQLite
- Manually written SQL queries

##  Project Structure
uis_connect_project/ │ ├── app/ │ ├── app.py │ ├── config.py │ ├── db_utils.py │ ├── static/ │ │ └── style.css │ └── templates/ │ ├── base.html │ ├── index.html │ ├── profile.html │ └── post.html │ ├── database/ │ ├── schema.sql │ ├── sample_data.sql │ └── queries.sql │ ├── docs/ │ ├── ER_diagram.png │ ├── normalization.pdf │ └── proposal.pdf │ └── README.md

# 📘 UIS-Connect: A Mini Social Network for Students

This project was developed as part of the **DAT220 – Databases** course at the University of Stavanger. The goal is to design a functional and normalized relational database and build a simple web application that allows interaction with that data.

UIS-Connect is a **campus-themed social media platform** that lets students:
- Create profiles
- Make posts
- Comment on posts
- Like content
- Add friends
- Explore a minimal social experience within a student community

---

## 👥 Group Members
**Group 36**
- Sture Troli
- Dennis Demaj

---

## 🛠 Tech Stack

| Layer         | Technology        |
|--------------|-------------------|
| Backend       | Python, Flask     |
| Database      | SQLite            |
| Frontend      | HTML, CSS (custom), Jinja2 templates |
| SQL Queries   | Manual SQL (no ORM or migration tools) |

---

## 🔍 Features

### Core Functionality
- 🔐 User registration and login/logout (session-based)
- 🧑 View your profile and posts
- 📝 Create new posts (Create)
- 💬 Comment on posts (Create + Read)
- 🧡 Like posts (Create + Count)
- 📑 See all recent posts (Read)
- 🔍 Filter posts by keyword (Search)
- 📈 Leaderboard of top posters (Aggregation + Grouping)
- 👥 View friend relationships (Join + Read)

### Bonus Features
- ✅ Flash messages (e.g. "Post created!", "Login failed")
- 📱 Responsive design (mobile-friendly)
- 🎨 Branding with UIS colors and logo
- 👤 Dynamic user avatars with ui-avatars.com
- 🔐 Protected routes (only logged-in users can post/comment)

---

## 🧠 How It Meets Project Requirements

| Requirement                  | Status      |
|-----------------------------|-------------|
| ≥ 5 normalized tables       | ✅ (Users, Posts, Comments, Likes, Friendships) |
| Manual SQL queries          | ✅ All queries written by hand |
| Joins (≥ 2)                 | ✅ Users + Posts, Users + Comments |
| Aggregation query           | ✅ Like counts, Post counts |
| Grouping query              | ✅ Posts per user |
| Filtering/searching         | ✅ By user, date, keyword |
| CRUD operations             | ✅ Posts and Comments (Create, Read, Delete/Edit coming soon) |
| Web Interface                | ✅ Flask-based app with HTML templates |
| Sample data (≥ 10 per table)| ✅ 10+ entries per table in `sample_data.sql` |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Odin-Troli19/UIS-CONNECT-PROJECT.git
cd uis-connect

Instructions:
00. (optional) - Set Up a Virtual Environment (Optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

3. Install Flask
pip install flask

4. Create and Populate the Database
python init_db.py          # Creates database and schema
python load_sample_data.py # Adds 10+ records per table

5. Run the App
python app/app.py

6. Open in Browser
Visit: http://127.0.0.1:5000

