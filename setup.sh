#!/bin/bash

# CAIA Travel Bot Setup Script
# This script creates a virtual environment and installs dependencies

echo "🌱 Setting up CAIA Travel Bot environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv travel_bot_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source travel_bot_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 To run your bot:"
echo "   1. source travel_bot_env/bin/activate"
echo "   2. streamlit run app_travel.py"
echo ""
echo "🛑 To deactivate the environment when done:"
echo "   deactivate"
