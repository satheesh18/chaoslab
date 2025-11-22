#!/bin/bash

# ChaosLab - Quick Start Script
# This script helps you get ChaosLab up and running quickly

set -e

echo "🧠 ChaosLab - Quick Start"
echo "========================="
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Check Node version
echo "📦 Checking Node.js version..."
node_version=$(node --version)
echo "   Found Node $node_version"
echo ""

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Backend dependencies installed"
cd ..

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "   Dependencies already installed"
fi
echo "✅ Frontend dependencies installed"
cd ..

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start ChaosLab:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:5173 in your browser!"
echo ""
