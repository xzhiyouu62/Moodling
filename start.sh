#!/bin/bash

# Activate environment
source venv/bin/activate

# Set environment
export FLASK_ENV=development
export FLASK_DEBUG=True

clear
echo "Moodling is ready at http://localhost:5001"
echo ""

# Start app
cd backend
python app.py
