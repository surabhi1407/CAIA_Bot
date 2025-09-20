#!/bin/bash

# CAIA Travel Bot Run Script
# Quick script to activate environment and run the Streamlit app

echo "🌱 Starting CAIA Travel Bot..."

# Check if virtual environment exists
if [ ! -d "travel_bot_env" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Creating template..."
    cat > .env << EOF
# Environment Variables for CAIA Travel Bot
# Add your actual OpenAI API key below
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo "📝 Please edit .env file and add your OpenAI API key before running again."
    exit 1
fi

# Activate virtual environment
source travel_bot_env/bin/activate

# Run Streamlit app
echo "🚀 Launching Streamlit app..."
streamlit run app_travel.py

echo "👋 Thanks for using CAIA Travel Bot!"
