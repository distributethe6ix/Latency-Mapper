# Latency Mapper - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │   Web Interface      │         │   CLI Interface      │    │
│  │  (templates/index)   │         │    (main.py)         │    │
│  │                      │         │                      │    │
│  │  - Interactive UI    │         │  - Command line      │    │
│  │  - Real-time updates │         │  - Batch processing  │    │
│  │  - Endpoint mgmt     │         │  - Demo mode         │    │
│  └──────────┬───────────┘         └──────────┬───────────┘    │
│             │                                │                 │
└─────────────┼────────────────────────────────┼─────────────────┘
              │                                │
              ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                   ┌─────────────────────┐                       │
│                   │  web_interface.py   │                       │
│                   │                     │                       │
│                   │  Flask REST API     │                       │
│                   │  - /api/endpoints   │                       │
│                   │  - /api/latency     │                       │
│                   │  - /api/map         │                       │
│                   └──────────┬──────────┘                       │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE MODULES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ latency_tester   │  │ map_visualizer   │  │graph_plotter │ │
│  │      .py         │  │      .py         │  │    .py       │ │
│  │                  │  │                  │  │              │ │
│  │ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────┐ │ │
│  │ │LatencyTester │ │  │ │  Latency     │ │  │ │ Latency  │ │ │
│  │ │              │ │  │ │    Map       │ │  │ │  Graph   │ │ │
│  │ │ - Threading  │ │  │ │ Visualizer   │ │  │ │ Plotter  │ │ │
│  │ │ - ICMP Ping  │ │  │ │              │ │  │ │          │ │ │
│  │ │ - History    │ │  │ │ - Folium map │ │  │ │ - Line   │ │ │
│  │ │ - Stats      │ │  │ │ - Arcs       │ │  │ │ - Heatmap│ │ │
│  │ └──────────────┘ │  │ │ - Markers    │ │  │ │ - Bars   │ │ │
│  │                  │  │ └──────────────┘ │  │ └──────────┘ │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL LIBRARIES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ping3  │  folium  │  matplotlib  │  flask  │  numpy/pandas    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Latency Measurement Flow

```
User adds endpoint
       │
       ▼
LatencyTester.start_monitoring()
       │
       ├─→ Creates background thread
       │
       └─→ Thread loop:
           ├─→ ping3.ping(target_ip)
           ├─→ Store result with timestamp
           ├─→ Sleep(interval)
           └─→ Repeat until stopped
```

### 2. Visualization Flow

```
User requests map
       │
       ▼
LatencyMapVisualizer
       │
       ├─→ Create folium.Map()
       ├─→ Add endpoint markers
       ├─→ For each connection:
       │   ├─→ Calculate arc path
       │   ├─→ Get latency color
       │   ├─→ Draw PolyLine
       │   └─→ Add AntPath animation
       │
       └─→ Save HTML file
```

### 3. Graph Generation Flow

```
User requests graphs
       │
       ▼
LatencyGraphPlotter
       │
       ├─→ Get history from LatencyTester
       ├─→ Extract timestamps & latencies
       ├─→ Create matplotlib figure
       │   ├─→ Plot lines/bars/heatmap
       │   ├─→ Add labels & legends
       │   └─→ Format axes
       │
       └─→ Save PNG file
```

## Component Details

### latency_tester.py

**Class**: `LatencyTester`

**Responsibilities**:
- Manage background threads for each endpoint
- Execute ICMP ping requests using ping3
- Store measurements with timestamps
- Calculate statistics (min/max/avg/success rate)
- Provide thread-safe access to data

**Key Methods**:
- `start_monitoring(id, ip, interval)` - Start monitoring thread
- `stop_monitoring(id)` - Stop specific monitor
- `get_latest_latency(id)` - Get most recent measurement
- `get_history(id)` - Get all measurements
- `get_statistics(id)` - Calculate stats

**Threading Model**:
- One daemon thread per endpoint
- Event-based stopping mechanism
- Thread-safe deque for data storage

### map_visualizer.py

**Class**: `LatencyMapVisualizer`

**Responsibilities**:
- Create interactive folium maps
- Render endpoints as markers
- Draw animated arcs between points
- Color-code by latency value
- Generate HTML output

**Key Methods**:
- `create_map()` - Initialize folium map
- `add_endpoint(id, name, lat, lon, ip)` - Add location
- `add_connection(source, target, latency)` - Add arc
- `render_map(path)` - Generate HTML

**Visualization Features**:
- Great circle arc calculations
- Color gradient (green → red)
- Animated "ant path" effect
- Interactive popups
- Fullscreen mode

### graph_plotter.py

**Class**: `LatencyGraphPlotter`

**Responsibilities**:
- Create historical latency graphs
- Support multiple chart types
- Export to PNG images
- Apply consistent styling

**Key Methods**:
- `plot_single_endpoint(history, name)` - Line graph
- `plot_multiple_endpoints(data)` - Comparison
- `plot_heatmap(data)` - Time-based heatmap
- `plot_statistics_bars(stats)` - Bar chart

**Chart Types**:
1. **Line Graph** - Latency over time
2. **Comparison** - Multiple endpoints
3. **Heatmap** - Color-coded matrix
4. **Statistics** - Min/avg/max bars

### web_interface.py

**Flask Application**

**Responsibilities**:
- Serve web UI
- Provide REST API
- Auto-update map in background
- Manage endpoint lifecycle

**API Endpoints**:
```
GET  /                      - Main page
GET  /api/endpoints/common  - Predefined endpoints
POST /api/source           - Set source location
POST /api/endpoints/add    - Add target endpoint
POST /api/endpoints/remove - Remove endpoint
GET  /api/endpoints/list   - List all endpoints
GET  /api/latency/current  - Current latency data
GET  /api/latency/history  - Historical data
POST /api/map/generate     - Generate map
GET  /api/map/view         - View generated map
```

**Background Tasks**:
- Auto-update map every 10 seconds
- Continuous latency monitoring per endpoint

### main.py

**CLI Application**

**Responsibilities**:
- Command-line interface
- Demo mode execution
- Batch processing
- Output generation

**Modes**:
1. **Demo Mode** - Predefined endpoints
2. **Custom Mode** - User-defined setup
3. **Web Mode** - Launch web interface

## File Structure

```
latency-mapper/
│
├── latency_tester.py      # Core measurement engine
├── map_visualizer.py      # Map rendering
├── graph_plotter.py       # Graph generation
├── web_interface.py       # Flask web server
├── main.py                # CLI entry point
│
├── requirements.txt       # Python dependencies
├── config.example.py      # Configuration template
├── run_demo.sh            # Quick start script
│
├── templates/
│   └── index.html         # Web UI template
│
├── static/                # Generated maps (created at runtime)
│
├── README.md              # User documentation
├── ARCHITECTURE.md        # This file
└── .gitignore            # Git ignore rules
```

## Threading and Concurrency

### Thread Management

```
Main Thread
    │
    ├─→ Flask Server Thread (web mode)
    │   ├─→ Request handlers (per request)
    │   └─→ Auto-update thread (background)
    │
    └─→ Monitoring Threads (one per endpoint)
        ├─→ Endpoint 1 thread
        ├─→ Endpoint 2 thread
        └─→ Endpoint N thread
```

### Thread Safety

- **deque** - Thread-safe queue for measurements
- **threading.Event** - Stop flag signaling
- **daemon=True** - Auto-cleanup on exit
- No shared mutable state between monitors

## Performance Characteristics

### Memory Usage

- ~1 KB per measurement
- 200 measurements default = 200 KB per endpoint
- Total memory ≈ N endpoints × 200 KB

### CPU Usage

- Minimal when idle
- Spike during ping operations
- Map rendering is I/O bound
- Graph plotting is CPU intensive

### Network Usage

- 64 bytes per ICMP ping (Echo Request)
- 64 bytes per ICMP pong (Echo Reply)
- At 2s interval: ~64 bytes/s per endpoint
- 10 endpoints = ~640 bytes/s

## Security Considerations

1. **ICMP Access**
   - Requires root/admin privileges
   - Raw socket creation (SOCK_RAW)
   - Potential security risk if compromised

2. **Web Interface**
   - Listens on 0.0.0.0 (all interfaces)
   - No authentication
   - CORS enabled
   - Input validation minimal

3. **Recommendations**
   - Run in isolated network segment
   - Use firewall rules for port 5000
   - Add authentication for production
   - Validate/sanitize all inputs
   - Consider rate limiting

## Extension Points

### Adding New Measurement Methods

Extend `LatencyTester` to support:
- TCP connection time
- HTTP request latency
- DNS lookup time
- Traceroute visualization

### Custom Visualizations

Extend `LatencyMapVisualizer`:
- Different map styles
- Custom markers/icons
- 3D globe view
- Route optimization

### Data Export

Add export methods:
- CSV format
- JSON format
- Prometheus metrics
- InfluxDB time series

### Real-time Updates

Replace polling with:
- WebSockets for live updates
- Server-Sent Events (SSE)
- Redis pub/sub
- Message queues

## Dependencies Graph

```
main.py
  ├─→ latency_tester.py
  │     └─→ ping3
  ├─→ map_visualizer.py
  │     └─→ folium
  └─→ graph_plotter.py
        └─→ matplotlib

web_interface.py
  ├─→ flask
  ├─→ latency_tester.py
  ├─→ map_visualizer.py
  └─→ templates/index.html
```

## Development Workflow

1. **Local Testing**
   ```bash
   python latency_tester.py  # Test measurement
   python map_visualizer.py  # Test visualization
   python graph_plotter.py   # Test graphing
   ```

2. **Demo Mode**
   ```bash
   sudo python3 main.py --duration 30
   ```

3. **Web Development**
   ```bash
   sudo python3 web_interface.py
   # Edit templates/index.html
   # Refresh browser
   ```

4. **Production Deployment**
   - Use gunicorn/uwsgi for Flask
   - Run behind nginx reverse proxy
   - Add authentication layer
   - Enable HTTPS

## Future Architecture Improvements

1. **Database Backend**
   - PostgreSQL/MySQL for storage
   - TimescaleDB for time-series data
   - Redis for caching

2. **Microservices**
   - Separate measurement service
   - Separate visualization service
   - API gateway

3. **Scalability**
   - Distributed monitoring agents
   - Message queue (RabbitMQ/Kafka)
   - Horizontal scaling

4. **Monitoring**
   - Health check endpoints
   - Metrics collection (Prometheus)
   - Logging (ELK stack)
   - Alerting (PagerDuty)
