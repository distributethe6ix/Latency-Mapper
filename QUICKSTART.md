# Quick Start Guide - Latency Mapper

Get up and running in 5 minutes!

## Installation

```bash
cd latency-mapper
pip install -r requirements.txt
```

## Option 1: Easy Start (Recommended)

Use the quick start script:

```bash
sudo ./run_demo.sh
```

Choose either:
1. **Web Interface** - Interactive browser-based UI
2. **CLI Demo** - Command-line batch processing

## Option 2: Web Interface

```bash
sudo python3 web_interface.py
```

Then open http://localhost:5000 in your browser.

### Using the Web Interface

1. **Set Source Location**
   - Enter your location name
   - Enter coordinates (or use defaults)
   - Click "Set Source Location"

2. **Add Target Endpoints**
   - Use "Quick Add" dropdown for common servers, OR
   - Enter custom endpoint details manually
   - Click "Add Target Endpoint"

3. **Monitor Results**
   - Watch real-time latency updates
   - View animated map with connection arcs
   - See live statistics at the bottom

## Option 3: CLI Demo

```bash
sudo python3 main.py
```

This runs a 60-second demo with predefined endpoints.

**Custom duration:**
```bash
sudo python3 main.py --duration 120 --interval 1.0
```

**Output files:**
- `latency_map.html` - Interactive map (open in browser)
- `latency_comparison.png` - Line graph
- `latency_statistics.png` - Bar chart
- `latency_heatmap.png` - Heatmap

## Common Issues

### "Operation not permitted"
You need root privileges for ICMP ping:
```bash
sudo python3 main.py
```

### "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Map shows gray connections
The target might be blocking ICMP. Try:
- Google DNS: 8.8.8.8
- Cloudflare DNS: 1.1.1.1

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Customize [config.example.py](config.example.py) for your needs

## Quick Examples

### Monitor Google DNS from San Francisco
```python
from latency_tester import LatencyTester

tester = LatencyTester()
tester.start_monitoring('google', '8.8.8.8', interval=1.0)

# Wait a bit...
import time
time.sleep(10)

# Get results
print(tester.get_statistics('google'))
```

### Create a Simple Map
```python
from map_visualizer import LatencyMapVisualizer

viz = LatencyMapVisualizer()
viz.add_endpoint('source', 'SF', 37.7, -122.4, '1.1.1.1', is_source=True)
viz.add_endpoint('target', 'London', 51.5, -0.1, '8.8.8.8')
viz.add_connection('source', 'target', 85.3)
viz.render_map('my_map.html')
```

### Plot Latency Graph
```python
from graph_plotter import LatencyGraphPlotter
from datetime import datetime, timedelta

plotter = LatencyGraphPlotter()

# Sample data
history = [
    {'timestamp': datetime.now() + timedelta(seconds=i),
     'latency': 50 + i*2,
     'success': True}
    for i in range(30)
]

plotter.plot_single_endpoint(history, 'Test Server', 'graph.png')
```

## That's It!

You're ready to map network latency. Have fun! 🚀
