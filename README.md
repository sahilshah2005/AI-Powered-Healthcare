# AI-Powered Healthcare Data Warehouse & Heart Disease Prediction System

A complete, production-ready full-stack web application designed as a final-year Computer Engineering project for Data Warehousing and Mining (DWM).

## Core Features
1. **Data Warehouse (Star Schema):** Built using Django ORM to integrate patient facts and categorical dimensions (Gender, Age Group, etc.).
2. **ETL Pipeline:** Automates extraction from raw CSV, cleaning missing values, normalizing data, and loading it into the Star Schema.
3. **Machine Learning Classification:** Integrates Decision Tree, Naïve Bayes, and Logistic Regression models. Features an **Explainable AI** module showing feature importance.
4. **Data Mining:** 
   - **K-Means Clustering:** Segments patients into risk groups based on continuous metrics.
   - **Apriori Algorithm:** Finds hidden association rules (e.g., High BP -> Heart Disease) using `mlxtend`.
5. **Interactive Dashboard:** Premium dark-themed UI built with Bootstrap 5 and Chart.js to visualize data distributions and model accuracy.
6. **Authentication:** Secure user registration and login system.

## Tech Stack
- **Backend:** Python, Django, Pandas, NumPy, Scikit-Learn, mlxtend, joblib
- **Frontend:** HTML5, CSS3, Bootstrap 5, Chart.js
- **Database:** SQLite (default) / PostgreSQL / MySQL ready

---

## 🚀 Quick Setup Guide

### 1. Requirements
Ensure you have Python 3.9+ installed.

### 2. Installation
Open your terminal and clone/navigate to the project directory:

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Migration & ETL Pipeline
We have packaged the Data Warehouse creation and ETL process into easy management commands.

```bash
# Create the database tables
python manage.py makemigrations
python manage.py migrate

# Run the ETL script to clean and load data into the Star Schema
python manage.py run_etl
```

### 4. Train Machine Learning Models
Generate the predictive models dynamically based on the newly loaded Data Warehouse facts.

```bash
python manage.py train_models
```

### 5. Run the Server
```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 📸 Usage Flow
1. **Landing Page:** View the project features.
2. **Register/Login:** Create a user account to access the system.
3. **Dashboard:** View data statistics, age distribution charts, and model comparison.
4. **Prediction:** Enter patient vitals to receive a risk probability score and feature importance graph.
5. **Data Mining:** View K-Means risk clusters and Apriori association rules.

---

## ⚙️ Switching to MySQL / PostgreSQL (Optional)
If your college requires a dedicated SQL server instead of SQLite:
1. Install `mysqlclient` (for MySQL) or `psycopg2` (for PostgreSQL) via `pip`.
2. Go to `core/settings.py`.
3. Update the `DATABASES` dictionary with your server credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # or postgresql
        'NAME': 'dwm_project',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
4. Run `python manage.py migrate` and `python manage.py run_etl` again.

---
**Designed for Final Year Computer Engineering Students.** Ready for viva and demonstration!
