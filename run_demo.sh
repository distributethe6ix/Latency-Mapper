#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           LATENCY MAPPER - Quick Start Demo             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: This script requires root privileges for ICMP ping."
    echo "   Please run with: sudo ./run_demo.sh"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Please choose a mode:"
echo ""
echo "  1) Interactive Web Interface (recommended)"
echo "  2) CLI Demo Mode"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Starting web interface..."
        echo "   Open http://localhost:5000 in your browser"
        echo ""
        echo "   Press Ctrl+C to stop"
        echo ""
        python3 web_interface.py
        ;;
    2)
        echo ""
        read -p "Enter monitoring duration in seconds (default: 30): " duration
        duration=${duration:-30}

        echo ""
        echo "🔍 Running CLI demo for $duration seconds..."
        python3 main.py --duration $duration --output demo

        echo ""
        echo "✓ Demo complete!"
        echo ""
        echo "Generated files:"
        echo "  - demo_map.html (open in browser)"
        echo "  - demo_comparison.png"
        echo "  - demo_statistics.png"
        echo "  - demo_heatmap.png"
        echo ""

        # Offer to open map
        read -p "Open the map in your browser? (y/n): " open_map
        if [ "$open_map" = "y" ]; then
            if command -v open &> /dev/null; then
                open demo_map.html
            elif command -v xdg-open &> /dev/null; then
                xdg-open demo_map.html
            else
                echo "Please open demo_map.html manually in your browser"
            fi
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
