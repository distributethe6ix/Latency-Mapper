# Setup From Scratch - Complete Guide

This guide will walk you through setting up the Latency Mapper from a fresh start.

## Step 1: Prerequisites

### Check Python Version

```bash
python3 --version
```

You need Python 3.7 or higher. If not installed:

**macOS:**
```bash
brew install python3
# or download from python.org
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Windows:**
Download from https://python.org and ensure "Add to PATH" is checked.

## Step 2: Navigate to Project

```bash
cd /Users/marino/latency-mapper
```

## Step 3: Install Dependencies

### Option A: System-wide Installation

```bash
pip3 install -r requirements.txt
```

### Option B: Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Verify Installation

Test each component:

```bash
# Test latency measurement (requires sudo)
sudo python3 -c "from latency_tester import LatencyTester; print('✓ Latency tester OK')"

# Test map visualization
python3 -c "from map_visualizer import LatencyMapVisualizer; print('✓ Map visualizer OK')"

# Test graph plotting
python3 -c "from graph_plotter import LatencyGraphPlotter; print('✓ Graph plotter OK')"

# Test web interface
python3 -c "from web_interface import app; print('✓ Web interface OK')"
```

## Step 5: Run Your First Test

### Quick CLI Demo

```bash
sudo python3 main.py --duration 30
```

This will:
1. Monitor latency to 4 predefined endpoints for 30 seconds
2. Generate an interactive map: `latency_map.html`
3. Create graphs: `latency_comparison.png`, `latency_statistics.png`, `latency_heatmap.png`

Open the map:
```bash
open latency_map.html  # macOS
```

## Step 6: Start Web Interface

### Default Port (5000)

```bash
sudo python3 web_interface.py
```

### Custom Port (if 5000 is in use)

```bash
sudo python3 web_interface.py --port 5001
```

Then open in browser: http://localhost:5001

## Step 7: Add Your First Endpoint

### In Web Interface:

1. **Set Source Location**
   - Fill in "Source Location" form
   - Enter your city or "My Location"
   - Add coordinates (see below for how to get them)
   - Click "Set Source Location"

2. **Add Target**
   - Use "Quick Add" dropdown for common servers, OR
   - Enter custom endpoint manually
   - Click "Add Target Endpoint"

3. **Watch Results**
   - Latency updates every 2 seconds
   - Map auto-refreshes every 10 seconds

## Getting Coordinates for Cities

### Method 1: Use the Geocoding Helper (see below)

We've added a geocoding script that converts city names to coordinates!

```bash
python3 geocode_helper.py "San Francisco"
# Output: San Francisco, CA, USA - Lat: 37.7749, Lon: -122.4194
```

### Method 2: Google Maps

1. Go to https://maps.google.com
2. Right-click on your location
3. Click the coordinates to copy them
4. Format: First number is latitude, second is longitude

### Method 3: Common Cities Reference

Here are coordinates for major cities:

**North America:**
- New York: `40.7128, -74.0060`
- Los Angeles: `34.0522, -118.2437`
- San Francisco: `37.7749, -122.4194`
- Chicago: `41.8781, -87.6298`
- Toronto: `43.6532, -79.3832`

**Europe:**
- London: `51.5074, -0.1278`
- Paris: `48.8566, 2.3522`
- Berlin: `52.5200, 13.4050`
- Amsterdam: `52.3676, 4.9041`
- Madrid: `40.4168, -3.7038`

**Asia:**
- Tokyo: `35.6762, 139.6503`
- Singapore: `1.3521, 103.8198`
- Hong Kong: `22.3193, 114.1694`
- Seoul: `37.5665, 126.9780`
- Mumbai: `19.0760, 72.8777`

**Oceania:**
- Sydney: `-33.8688, 151.2093`
- Melbourne: `-37.8136, 144.9631`
- Auckland: `-36.8485, 174.7633`

**South America:**
- São Paulo: `-23.5505, -46.6333`
- Buenos Aires: `-34.6037, -58.3816`
- Rio de Janeiro: `-22.9068, -43.1729`

**Africa:**
- Cairo: `30.0444, 31.2357`
- Johannesburg: `-26.2041, 28.0473`
- Lagos: `6.5244, 3.3792`

## Auto-Detecting Your Location

### Method 1: Using IP Geolocation API

We've added an auto-detect script!

```bash
python3 location_detector.py
```

This will automatically detect your location based on your public IP.

### Method 2: Browser Geolocation (Web Interface)

The web interface can request your browser's location (requires HTTPS in production).

### Method 3: System Location Services (macOS)

```bash
# macOS only - requires location services enabled
python3 -c "import urllib.request, json; print(json.loads(urllib.request.urlopen('https://ipapi.co/json/').read())['city'])"
```

## Common Scenarios

### Scenario 1: Monitor Cloud Regions from Your Office

```bash
# Start web interface
sudo python3 web_interface.py --port 5001

# In browser:
# 1. Set source: "My Office, San Francisco" (37.7749, -122.4194)
# 2. Quick add: AWS regions (us-east, us-west, europe, asia-pacific)
# 3. Watch latency to different cloud regions
```

### Scenario 2: Test CDN Performance

```bash
# CLI mode with specific targets
sudo python3 main.py --duration 120

# Modify main.py to test Cloudflare, Fastly, Akamai edge locations
```

### Scenario 3: Monitor Game Servers

```bash
# Add your favorite game server locations
# Example: Valorant, Fortnite, LoL servers
```

## Troubleshooting Setup

### "pip3: command not found"

```bash
# macOS
python3 -m ensurepip

# Linux
sudo apt install python3-pip

# Verify
pip3 --version
```

### "No module named 'ping3'"

```bash
# Install dependencies
pip3 install -r requirements.txt

# If still fails, install individually
pip3 install ping3 folium matplotlib flask flask-cors numpy pandas
```

### "Operation not permitted" (ICMP ping)

You MUST use `sudo` for ICMP ping:

```bash
sudo python3 main.py
sudo python3 web_interface.py
```

### Port 5000 already in use

```bash
# Use different port
sudo python3 web_interface.py --port 5001

# Or kill existing process
lsof -ti:5000 | xargs kill -9
```

### Virtual environment issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. **Read the docs:**
   - [QUICKSTART.md](QUICKSTART.md) - 5-minute guide
   - [README.md](README.md) - Full documentation
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

2. **Customize:**
   - Edit `config.example.py` and save as `config.py`
   - Modify `COMMON_ENDPOINTS` in `map_visualizer.py`

3. **Experiment:**
   - Try different ping intervals
   - Add custom endpoints
   - Export graphs

4. **Share:**
   - Deploy to a server for team access
   - Add authentication
   - Set up continuous monitoring

## Quick Commands Cheat Sheet

```bash
# Install
pip3 install -r requirements.txt

# CLI demo (30 seconds)
sudo python3 main.py --duration 30

# CLI custom duration
sudo python3 main.py --duration 120 --interval 1.0 --output my_test

# Web interface (port 5001)
sudo python3 web_interface.py --port 5001

# Geocode a city
python3 geocode_helper.py "Tokyo"

# Auto-detect location
python3 location_detector.py

# Test individual components
python latency_tester.py
python map_visualizer.py
python graph_plotter.py

# Virtual environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Help & Support

- **Issues:** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Examples:** See [QUICKSTART.md](QUICKSTART.md)
- **Architecture:** Read [ARCHITECTURE.md](ARCHITECTURE.md)

---

**You're all set!** 🚀 Start monitoring network latency!
