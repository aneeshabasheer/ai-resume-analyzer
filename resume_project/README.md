# AI Resume Analyzer

A Python Full Stack Web Application powered by Django, NLP (spaCy), Machine Learning (Scikit-Learn TF-IDF + Cosine Similarity), and Bootstrap 5. 

This project is designed as a **final-year computer science project** (BCA, BSc, MCA, B.Tech) for students to easily understand, deploy, and explain during their viva-voce examinations.

---

## 🚀 Key Features

1. **User Authentication**: Standard Django auth (Register, Login, Session Management, Logout).
2. **Candidate Dashboard**: Overview of uploaded resumes, match scores, recent analysis list, and progress indicators.
3. **NLP Resume Parser**: Extracts Email, Phone, Candidate Name (using spaCy NER), and matches technical skills against a comprehensive list from PDF/DOCX documents.
4. **TF-IDF Job Matcher**: Uses TF-IDF Text Vectorization and Cosine Similarity to calculate the matching index against active job posts.
5. **Chart.js Analytics**: A bar chart comparing the candidate's skills against four classic industry roles (Python Developer, Backend Developer, Data Analyst, Machine Learning Engineer).
6. **Career Chatbot**: A rule-based helper chatbot addressing questions on resumes, Python, Django MVT, and interview preparation. Keeps records in `ChatHistory`.
7. **Job CRUD Panel**: Admin/Staff view allowing creation, updating, and removal of job descriptions.
8. **Candidate Profile**: Custom avatar uploading, manually updating skills, education summary, and biography text.
9. **Analysis History Table**: Full log of all uploaded resumes and their score summaries.
10. **Report Downloader**: Allows downloading clean text-based summaries of analysis results.

---

## 🛠️ Tech Stack & Libraries

- **Backend**: Python 3.x, Django 4.x
- **Database**: SQLite (default for instant running) / PostgreSQL (configured and ready for deployment)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (ES6+), Chart.js
- **Key Libraries**:
  - `pdfplumber` (PDF extraction)
  - `python-docx` (DOCX extraction)
  - `spacy` (Named Entity Recognition - Name parsing)
  - `scikit-learn` (TF-IDF vectorizer and Cosine Similarity equations)
  - `pandas`, `numpy` (data structure parsing)

---

## ⚙️ Project Setup Guide

### 1. Setup Virtual Environment (Recommended)
Open your terminal in the project directory:
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install spaCy NLP Model
To enable spaCy Named Entity Recognition for parsing names:
```bash
python -m spacy download en_core_web_sm
```
*Note: The code contains a fallback parser that extracts details correctly even if the spaCy language model is not downloaded.*

### 4. Setup Database & Migrations
Create standard tables in the database:
```bash
python manage.py makemigrations resume_app
python manage.py migrate
```

### 5. Create Superuser (Admin Account)
Create a superuser to access the Django admin portal and manage job listings:
```bash
python manage.py createsuperuser
```
Follow the prompts (Username, Email, Password).

### 6. Run the Project
Start the local development server:
```bash
python manage.py runserver
```
Visit the project at: **http://127.0.0.1:8000/**

---

## 🐘 Configuring PostgreSQL

By default, the project runs on **SQLite** for zero-setup execution. To connect your local **PostgreSQL** database:

1. Open `config/settings.py`.
2. Locate the database config section.
3. Switch the environment variable `USE_POSTGRESQL=True` or modify `settings.py` directly:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'resume_analyzer_db',
           'USER': 'postgres',
           'PASSWORD': 'your_postgres_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
4. Create the database in PostgreSQL:
   ```sql
   CREATE DATABASE resume_analyzer_db;
   ```
5. Rerun migrations to create tables in PostgreSQL:
   ```bash
   python manage.py migrate
   ```

---

## 💡 Viva Questions & Core Concepts

For college project defense / viva exams:

### 1. How does the NLP parsing work?
The file `resume_app/resume_parser.py` loads the PDF or DOCX file. It reads pages line by line. It runs RegEx patterns to match emails and telephone patterns. For names, it uses spaCy's `PERSON` Entity Tag. For skills, it scans the text block for occurrences of technical terms defined in `COMMON_SKILLS`.

### 2. Explain the Job Matching Math.
The script `resume_app/utils.py` computes a match score:
- **Cosine Similarity**: Vectorizes both the resume text and the job description combined text using `TfidfVectorizer`. The vectorizer represents text as coordinates based on word frequencies. Cosine Similarity calculates the angle between these vectors.
- **Skill Overlap**: Computes what percentage of required job skills are found in the resume.
- **Hybrid Score**: Combines 60% Skill Overlap + 40% Cosine Similarity to output a realistic score between 0 and 100.

### 3. What is Django MVT?
- **Model**: Python classes in `models.py` mapping to database tables.
- **View**: Logic in `views.py` that processes user requests, fetches data from Models, and passes context to templates.
- **Template**: HTML layout files in `templates/` that render the frontend to users.
