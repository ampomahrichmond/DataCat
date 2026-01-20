#!/bin/bash

# Alteryx to Python Converter - Startup Script
echo "🔄 Starting Alteryx to Python Converter..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ All dependencies are ready!"
echo ""
echo "🚀 Launching application..."
echo "📍 The app will open in your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Launch the app
streamlit run app.py
