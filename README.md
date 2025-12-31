# 🌍 Latency Mapper

A powerful, interactive network latency visualization tool that displays real-time ping measurements on a world map with animated connection arcs and historical graphs.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

✨ **Real-Time Latency Monitoring** - Continuous ICMP ping measurements with automatic updates
🗺️ **Interactive World Map** - Beautiful folium-based visualization with wide atlas view
🎨 **Animated Connection Arcs** - Color-coded arcs showing latency (green=fast, red=slow)
📊 **Historical Graphs** - Multiple chart types including line graphs, heatmaps, and statistics
🎯 **Multiple Endpoints** - Monitor latency to multiple targets simultaneously
🖱️ **Interactive Selection** - Web-based UI for easy endpoint management
📈 **Real-Time Statistics** - Live updates of min/max/average latency

## Architecture

The application consists of several modular components:

- **latency_tester.py** - Core latency measurement engine using ping3
- **map_visualizer.py** - World map rendering with folium and animated arcs
- **graph_plotter.py** - Historical data visualization with matplotlib
- **web_interface.py** - Flask-based web server for interactive UI
- **main.py** - CLI interface and demo mode

## Installation

### Prerequisites

- Python 3.7 or higher
- Root/admin privileges (required for ICMP ping)

### Setup

```bash
cd latency-mapper
pip install -r requirements.txt
```

## Usage

### Option 1: Interactive Web Interface (Recommended)

Start the web server with root privileges:

```bash
sudo python3 web_interface.py
```

Then open your browser to `http://localhost:5000`

**Web Interface Features:**
- Click-to-add endpoints on the map
- Real-time latency updates every 2 seconds
- Auto-refreshing map visualization
- Quick-add common server locations
- Live statistics dashboard

### Option 2: Command Line Interface

Run the demo mode:

```bash
sudo python3 main.py
```

**CLI Options:**
```bash
sudo python3 main.py --duration 120 --interval 1.0 --output my_test
```

- `--duration`: Monitoring duration in seconds (default: 60)
- `--interval`: Ping interval in seconds (default: 2.0)
- `--output`: Output file prefix (default: latency)

### Option 3: Python API

Use the modules programmatically:

```python
from latency_tester import LatencyTester
from map_visualizer import LatencyMapVisualizer
from graph_plotter import LatencyGraphPlotter

# Initialize
tester = LatencyTester()
visualizer = LatencyMapVisualizer()
plotter = LatencyGraphPlotter()

# Add endpoints
visualizer.add_endpoint('source', 'My Location', 37.7, -122.4, '8.8.8.8', is_source=True)
visualizer.add_endpoint('target1', 'London', 51.5, -0.1, '8.8.8.8')

# Start monitoring
tester.start_monitoring('target1', '8.8.8.8', interval=2.0)

# ... wait for data collection ...

# Get results
latency = tester.get_latest_latency('target1')
stats = tester.get_statistics('target1')
history = tester.get_history('target1')

# Generate visualizations
visualizer.add_connection('source', 'target1', latency)
visualizer.render_map('output_map.html')

plotter.plot_single_endpoint(history, 'London', 'output_graph.png')
```

## How It Works

### 1. Latency Measurement

The `LatencyTester` class uses the `ping3` library to send ICMP Echo Request packets and measure round-trip time:

- Spawns background threads for each endpoint
- Continuously pings at specified intervals
- Stores historical data with timestamps
- Calculates statistics (min/max/average/success rate)

### 2. Map Visualization

The `LatencyMapVisualizer` creates interactive maps using folium:

- Uses CartoDB Positron tiles for clean world atlas view
- Draws great circle arcs between endpoints
- Color codes connections based on latency:
  - Green: < 50ms (excellent)
  - Yellow-Green: 50-100ms (good)
  - Yellow: 100-150ms (moderate)
  - Orange: 150-200ms (slow)
  - Red: > 200ms (very slow)
  - Gray: Connection failed
- Adds animated "ant path" effect for visual interest
- Includes interactive popups with latency details

### 3. Historical Graphing

The `LatencyGraphPlotter` creates various chart types:

- **Line graphs** - Latency over time for single or multiple endpoints
- **Heatmaps** - Color-coded latency matrix across time
- **Bar charts** - Statistical comparison across endpoints
- Uses matplotlib with seaborn styling

### 4. Web Interface

The Flask-based web interface provides:

- REST API for endpoint management
- Real-time latency updates via polling
- Auto-refreshing map display
- Interactive endpoint addition/removal
- Live statistics dashboard

## Output Files

The tool generates several output files:

- `*_map.html` - Interactive world map (open in browser)
- `*_comparison.png` - Line graph comparing all endpoints
- `*_statistics.png` - Bar chart of latency statistics
- `*_heatmap.png` - Heatmap of latency over time

## Common Endpoints

The tool includes predefined locations for popular servers:

- US East (Virginia) - AWS region
- US West (California) - AWS region
- Europe (Ireland) - AWS region
- Asia Pacific (Singapore) - AWS region
- South America (São Paulo) - AWS region
- Australia (Sydney) - AWS region
- Google DNS (8.8.8.8)
- Cloudflare DNS (1.1.1.1)

## Troubleshooting

### "Operation not permitted" error

ICMP ping requires root privileges. Run with `sudo`:
```bash
sudo python3 main.py
```

### Map not displaying

Check that the HTML file was generated and open it directly in a browser:
```bash
open latency_map.html  # macOS
xdg-open latency_map.html  # Linux
start latency_map.html  # Windows
```

### High latency or timeouts

- Check your internet connection
- Verify the target IP/hostname is reachable
- Some servers block ICMP ping - try alternative targets
- Firewall may be blocking ICMP packets

### Web interface not loading

- Ensure Flask is running: `sudo python3 web_interface.py`
- Check firewall settings for port 5000
- Try accessing via `http://127.0.0.1:5000` instead of localhost

## Performance Considerations

- **Ping Interval**: Lower intervals (< 1s) provide more data but increase network traffic
- **History Size**: Default is 200 measurements per endpoint (configurable in LatencyTester)
- **Multiple Endpoints**: Each endpoint runs in a separate thread
- **Map Rendering**: Auto-updates every 10 seconds in web mode

## Security Notes

- **Root Privileges**: Required for raw socket access (ICMP)
- **Web Interface**: Runs on 0.0.0.0 - accessible from network
- **CORS**: Enabled for API access - restrict in production
- **Input Validation**: Minimal - sanitize inputs for production use

## Technical Details

### Dependencies

- **ping3** - ICMP ping implementation
- **folium** - Interactive map visualization
- **matplotlib** - Static graph plotting
- **flask** - Web server framework
- **numpy/pandas** - Data processing

### Threading Model

- Main thread handles Flask web server
- Separate daemon threads for each endpoint monitor
- Thread-safe data structures (deque) for measurements
- Event-based stop flags for clean shutdown

### Data Structure

Each measurement stores:
```python
{
    'timestamp': datetime,
    'latency': float,  # milliseconds
    'success': bool
}
```

## Future Enhancements

Potential improvements:
- [ ] TCP/HTTP latency testing (alternative to ICMP)
- [ ] Traceroute visualization
- [ ] Packet loss tracking
- [ ] WebSocket for real-time updates (instead of polling)
- [ ] Database backend for persistent storage
- [ ] Export data to CSV/JSON
- [ ] Mobile-responsive UI
- [ ] Dark mode
- [ ] Custom map markers and styles
- [ ] Geolocation API for auto-detecting source

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions welcome! Please open an issue or pull request.

## Credits

Built with:
- [Folium](https://python-visualization.github.io/folium/) - Map visualization
- [ping3](https://github.com/kyan001/ping3) - Python ping implementation
- [Matplotlib](https://matplotlib.org/) - Graph plotting
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

**Note**: This tool is intended for network diagnostics and educational purposes. Please respect network policies and rate limits when testing external servers.
