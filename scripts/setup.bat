@echo off
REM Setup script for AI Resume Screening System (Windows)

echo Setting up AI Resume Screening System...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Download spaCy model
echo Downloading spaCy model...
python scripts\download_spacy_model.py

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please update .env with your database credentials!
)

REM Initialize database
echo Initializing database...
python scripts\init_db.py

echo Setup complete!
echo To start the server, run: uvicorn app.main:app --reload

