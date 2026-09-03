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
echo [2/5] Checking and Installing Dependencies...
pip install -r requirements.txt --quiet

echo.
echo [3/5] Applying Database Migrations...
python manage.py migrate

echo.
echo [4/5] Checking Data Warehouse Initialization...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from etl.models import PatientFact; print('Loaded count:', PatientFact.objects.count()); exit(0 if PatientFact.objects.exists() else 1)"
IF %ERRORLEVEL% NEQ 0 (
    echo Populating Data Warehouse via ETL...
    python manage.py run_etl
) ELSE (
    echo Data Warehouse records already initialized.
)

IF NOT EXIST "models\RandomForestClassifier.pkl" (
    echo Training Machine Learning Model Pipelines...
    python manage.py train_models
) ELSE (
    echo Machine learning model artifacts already trained.
)

echo.
echo [5/5] Starting Django Development Server at http://127.0.0.1:8000/
start "" http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000

pause
