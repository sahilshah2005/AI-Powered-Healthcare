@echo off
echo ========================================================
echo   AI-Powered Healthcare Data Warehouse System Start-Up
echo ========================================================

echo.
echo [1/5] Checking and activating Virtual Environment...
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [2/5] Installing Dependencies...
pip install -r requirements.txt --quiet

echo.
echo [3/5] Applying Database Migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo [4/5] Running ETL Pipeline and Training ML Models...
python manage.py run_etl
python manage.py train_models

echo.
echo [5/5] Starting Django Development Server...
start "" http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000

pause
