"""
Example configuration file for Latency Mapper.
Copy this to config.py and customize as needed.
"""

# Monitoring settings
PING_INTERVAL = 2.0  # Seconds between pings
MAX_HISTORY = 200    # Maximum measurements to keep per endpoint
PING_TIMEOUT = 2.0   # Timeout for each ping in seconds

# Web interface settings
WEB_HOST = '0.0.0.0'  # Listen on all interfaces
WEB_PORT = 5000       # Port for web interface
DEBUG_MODE = False    # Set to True for development

# Map visualization settings
MAP_CENTER = (20, 0)  # Default map center (lat, lon)
MAP_ZOOM = 2          # Initial zoom level
MAP_TILES = 'CartoDB positron'  # Map style

# Color thresholds for latency (in milliseconds)
COLOR_EXCELLENT = 50   # Green
COLOR_GOOD = 100       # Yellow-green
COLOR_MODERATE = 150   # Yellow
COLOR_SLOW = 200       # Orange
# Above COLOR_SLOW = Red

# Graph settings
GRAPH_FIGSIZE = (12, 6)  # Figure size in inches
GRAPH_DPI = 150          # Resolution for saved images
GRAPH_STYLE = 'seaborn-v0_8-darkgrid'  # Matplotlib style

# Auto-update intervals (web interface)
MAP_AUTO_UPDATE_INTERVAL = 10    # Seconds
LATENCY_POLL_INTERVAL = 2        # Seconds

# Custom endpoint presets (add your own)
CUSTOM_ENDPOINTS = {
    'my_server': {
        'name': 'My Custom Server',
        'lat': 40.7128,
        'lon': -74.0060,
        'ip': '203.0.113.1'
    },
    # Add more custom endpoints here
}
