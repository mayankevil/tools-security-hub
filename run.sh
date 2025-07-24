#!/bin/bash

cd backend

if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

echo "Creating virtual environment..."
python3 -m venv venv

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
