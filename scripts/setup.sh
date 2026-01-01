#!/bin/bash

# Setup script for AI Resume Screening System

echo "Setting up AI Resume Screening System..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python scripts/download_spacy_model.py

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please update .env with your database credentials!"
fi

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

echo "Setup complete!"
echo "To start the server, run: uvicorn app.main:app --reload"

