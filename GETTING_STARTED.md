# Getting Started - Zero to Running in 5 Minutes

Complete beginner's guide to get the Latency Mapper up and running.

## Prerequisites Check

```bash
# Check Python version (need 3.7+)
python3 --version

# Check pip
pip3 --version
```

If missing, install Python from https://python.org

## Installation (2 minutes)

```bash
# Navigate to the project
cd /Users/marino/latency-mapper

# Install dependencies
pip3 install -r requirements.txt
```

That's it! You're ready to run.

## Running Options

### 🌐 **Option 1: Web Interface** (Recommended for beginners)

```bash
sudo python3 web_interface.py --port 5001
```

Then open http://localhost:5001 in your browser.

**In the web interface:**

1. **Click "🌍 Auto-Detect My Location"**
   - Automatically fills in your coordinates
   - No manual entry needed!

2. **Or type a city name:**
   - Type "Tokyo" or "London, UK" in the source location field
   - Click "📍 Find Coordinates"
   - Coordinates auto-fill!

3. **Add targets:**
   - Use the dropdown to select common servers (Google DNS, AWS regions, etc.)
   - Or add custom endpoints

4. **Watch live results:**
   - Latency updates every 2 seconds
   - Map refreshes automatically
   - See real-time statistics

### 💻 **Option 2: Command Line** (Quick demo)

```bash
sudo python3 main.py --duration 30
```

This runs a 30-second demo and creates:
- `latency_map.html` - Open this in your browser!
- `latency_comparison.png`
- `latency_statistics.png`
- `latency_heatmap.png`

## Using the Utilities

### Auto-Detect Your Location

```bash
python3 location_detector.py
```

Output example:
```
============================================================
YOUR CURRENT LOCATION
============================================================
IP Address:    70.27.207.227
City:          Whitby, Ontario
Country:       Canada (CA)
Coordinates:   43.8762, -78.9261
============================================================
```

Copy the lat/lon values to use in the web interface!

### Convert City to Coordinates

```bash
python3 geocode_helper.py "Tokyo, Japan"
```

Output example:
```
============================================================
Location: 東京都, 日本
============================================================
Latitude:  35.6769
Longitude: 139.7639
============================================================
```

### Interactive Geocoding

```bash
python3 geocode_helper.py --interactive
```

Then type city names one by one:
```
Location: Paris
✓ Found: Paris, Île-de-France, France métropolitaine, France
  Latitude:  48.8566
  Longitude: 2.3522

Location: Sydney
✓ Found: Sydney, New South Wales, Australia
  Latitude:  -33.8688
  Longitude: 151.2093

Location: quit
```

### Batch Geocode Multiple Cities

```bash
python3 geocode_helper.py --batch "New York" "London" "Tokyo"
```

## Common Workflows

### Workflow 1: Monitor from your location to cloud regions

```bash
# Start web interface
sudo python3 web_interface.py --port 5001

# In browser:
# 1. Click "Auto-Detect My Location"
# 2. Select cloud regions from dropdown:
#    - US East (Virginia)
#    - US West (California)
#    - Europe (Ireland)
#    - Asia Pacific (Singapore)
# 3. Click "Add Target Endpoint" for each
# 4. Watch latency in real-time!
```

### Workflow 2: Compare latency from a specific city

```bash
# Start web interface
sudo python3 web_interface.py --port 5001

# In browser:
# 1. Type "Tokyo, Japan" in source location
# 2. Click "Find Coordinates"
# 3. Add targets (Google DNS, Cloudflare DNS, etc.)
# 4. See how latency differs from Tokyo
```

### Workflow 3: Create a quick report

```bash
# Run 2-minute test
sudo python3 main.py --duration 120 --output my_report

# Open results
open my_report_map.html
open my_report_comparison.png
open my_report_statistics.png
```

## Major Cities Quick Reference

Just copy-paste these into the web interface:

**North America:**
- San Francisco: `37.7749, -122.4194`
- New York: `40.7128, -74.0060`
- Toronto: `43.6532, -79.3832`

**Europe:**
- London: `51.5074, -0.1278`
- Paris: `48.8566, 2.3522`
- Berlin: `52.5200, 13.4050`

**Asia:**
- Tokyo: `35.6762, 139.6503`
- Singapore: `1.3521, 103.8198`
- Mumbai: `19.0760, 72.8777`

**Oceania:**
- Sydney: `-33.8688, 151.2093`
- Melbourne: `-37.8136, 144.9631`

## Troubleshooting

### "Operation not permitted"

You need `sudo` for ping:
```bash
sudo python3 web_interface.py --port 5001
```

### "Port 5000 already in use"

Use a different port:
```bash
sudo python3 web_interface.py --port 5001
```

### "Module not found"

Install dependencies:
```bash
pip3 install -r requirements.txt
```

### Location detection not working

Try manually:
```bash
python3 location_detector.py
```

If that fails, use Google Maps:
1. Go to https://maps.google.com
2. Right-click on your location
3. Click the coordinates to copy

## Next Steps

- ✅ You now know how to run the tool!
- 📖 Read [SETUP_FROM_SCRATCH.md](SETUP_FROM_SCRATCH.md) for detailed setup
- 🚀 Read [QUICKSTART.md](QUICKSTART.md) for more features
- 📚 Read [README.md](README.md) for full documentation

## Quick Command Reference

```bash
# Web interface (recommended)
sudo python3 web_interface.py --port 5001

# CLI demo (30 seconds)
sudo python3 main.py --duration 30

# Auto-detect location
python3 location_detector.py

# Convert city to coordinates
python3 geocode_helper.py "Paris, France"

# Interactive geocoding
python3 geocode_helper.py --interactive

# Test individual modules
python3 latency_tester.py
python3 map_visualizer.py
python3 graph_plotter.py
```

---

**You're all set! Have fun mapping network latency!** 🚀🌍
