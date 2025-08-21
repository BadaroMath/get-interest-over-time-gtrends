#!/bin/bash
# Google Trends Analyzer Installation Script

set -e

echo "🚀 Installing Google Trends Analyzer..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📥 Installing Google Trends Analyzer..."
pip install -e .

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install -e ".[dev]"
    
    # Install pre-commit hooks
    echo "⚙️ Setting up pre-commit hooks..."
    pre-commit install
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p results cache logs config

# Copy example configuration
if [ ! -f "config/config.yaml" ]; then
    echo "📄 Creating default configuration..."
    cp config/default.yaml config/config.yaml
fi

echo "✅ Installation completed successfully!"
echo ""
echo "🎯 Quick start:"
echo "   source venv/bin/activate"
echo "   trends-analyzer --help"
echo ""
echo "📖 Example usage:"
echo "   trends-analyzer analyze -k 'python programming' -g US -t 'today 3-m'"
echo ""
echo "🔧 Configuration:"
echo "   Edit config/config.yaml to customize settings"