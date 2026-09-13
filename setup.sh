#!/bin/bash

# Exit immediately if any command fails
set -e

echo "🚀 Starting environment setup..."

# 1. Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install it to continue."
    exit 1
fi

# 2. Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

# 3. Activate the virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# 4. Upgrade pip inside the environment
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# 5. Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

echo "✅ Setup complete!"
echo "🖥️ Starting Streamlit application..."

# 6. Run your Streamlit app (change app.py to your filename)
streamlit run aschedulingapp_fullstack.py
