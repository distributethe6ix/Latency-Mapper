# Troubleshooting Guide

Common issues and their solutions.

## Installation Issues

### "pip: command not found"

**Solution:**
```bash
# macOS/Linux
python3 -m ensurepip
python3 -m pip install -r requirements.txt

# Or install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### "ModuleNotFoundError: No module named 'ping3'"

**Solution:**
```bash
pip install -r requirements.txt

# If that fails, install individually:
pip install ping3 folium matplotlib flask flask-cors numpy pandas
```

### "error: externally-managed-environment"

Modern Python restricts system-wide installs. Use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## Permission Issues

### "Operation not permitted" / "Permission denied"

ICMP ping requires root/admin privileges.

**macOS/Linux:**
```bash
sudo python3 main.py
# or
sudo python3 web_interface.py
```

**Windows:**
Run Command Prompt or PowerShell as Administrator:
```powershell
python3 main.py
```

**Alternative (no root):**

Modify the code to use TCP instead of ICMP:
```python
# In latency_tester.py, replace ping3 with socket-based approach
import socket
import time

def tcp_ping(host, port=80, timeout=2):
    start = time.time()
    try:
        socket.create_connection((host, port), timeout=timeout)
        return (time.time() - start) * 1000
    except:
        return None
```

## Runtime Errors

### "All pings failed" / Gray connections

**Possible causes:**
1. Target blocks ICMP
2. Firewall blocking outgoing ICMP
3. Network connectivity issues
4. Wrong IP address

**Solutions:**

1. **Try different targets:**
   ```python
   # Known to accept ICMP:
   - 8.8.8.8 (Google DNS)
   - 1.1.1.1 (Cloudflare DNS)
   - 208.67.222.222 (OpenDNS)
   ```

2. **Check firewall:**
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

   # Linux
   sudo iptables -L OUTPUT | grep icmp

   # Windows
   netsh advfirewall show allprofiles
   ```

3. **Test manually:**
   ```bash
   ping -c 4 8.8.8.8  # Linux/macOS
   ping -n 4 8.8.8.8  # Windows
   ```

### "Address already in use" (port 5000)

**Solution:**

Kill existing process:
```bash
# Find process
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill it
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
python3 web_interface.py --port 5001
```

### "Cannot connect to Flask server"

**Solutions:**

1. **Check if server is running:**
   ```bash
   curl http://localhost:5000
   ```

2. **Try 127.0.0.1 instead of localhost:**
   ```
   http://127.0.0.1:5000
   ```

3. **Check firewall allows port 5000**

4. **Use different port:**
   Edit web_interface.py:
   ```python
   app.run(debug=True, host='0.0.0.0', port=8080)
   ```

## Visualization Issues

### Map not rendering / Blank page

**Solutions:**

1. **Check browser console** (F12) for JavaScript errors

2. **Verify HTML was generated:**
   ```bash
   ls -lh latency_map.html
   # Should be > 10KB
   ```

3. **Open file directly:**
   ```bash
   open latency_map.html  # macOS
   xdg-open latency_map.html  # Linux
   start latency_map.html  # Windows
   ```

4. **Try different browser** (Chrome, Firefox, Safari)

5. **Check for CORS issues** in web mode:
   - Should not affect local file viewing
   - May affect web interface

### Graphs not displaying

**Solutions:**

1. **Check matplotlib backend:**
   ```python
   import matplotlib
   print(matplotlib.get_backend())

   # If 'agg' not available, install:
   pip install matplotlib --force-reinstall
   ```

2. **Verify image files exist:**
   ```bash
   ls -lh *.png
   ```

3. **Check file permissions:**
   ```bash
   chmod 644 *.png
   ```

### Coordinates not showing correctly

**Solutions:**

1. **Verify lat/lon format:**
   - Latitude: -90 to 90 (negative = South)
   - Longitude: -180 to 180 (negative = West)

2. **Example coordinates:**
   ```
   San Francisco: 37.7749, -122.4194
   London: 51.5074, -0.1278
   Tokyo: 35.6762, 139.6503
   Sydney: -33.8688, 151.2093
   ```

## Performance Issues

### High CPU usage

**Causes & Solutions:**

1. **Too many endpoints:**
   - Reduce to < 20 simultaneous endpoints
   - Increase ping interval

2. **Interval too short:**
   ```python
   tester.start_monitoring(id, ip, interval=5.0)  # 5 seconds instead of 1
   ```

3. **Graph rendering:**
   - Normal - spikes during render
   - Reduce history size in config

### Memory usage growing

**Solutions:**

1. **Limit history size:**
   ```python
   tester = LatencyTester(max_history=100)  # Default is 200
   ```

2. **Clear old data periodically:**
   ```python
   tester.measurements[endpoint_id].clear()
   ```

### Slow map rendering

**Solutions:**

1. **Reduce number of arc points:**
   ```python
   # In map_visualizer.py
   arc_points = self._create_arc_coordinates(
       start, end, num_points=50  # Default is 100
   )
   ```

2. **Simplify map:**
   ```python
   # Use simpler tile layer
   m = folium.Map(tiles='OpenStreetMap')  # Instead of CartoDB
   ```

## Data Issues

### Latency values seem wrong

**Verify:**

1. **Units are correct:**
   - Displayed in milliseconds (ms)
   - ping3 returns seconds - we multiply by 1000

2. **Check actual latency:**
   ```bash
   ping -c 10 8.8.8.8
   ```

3. **Network conditions:**
   - WiFi vs Ethernet
   - VPN active?
   - Background downloads?

### No historical data

**Solutions:**

1. **Wait for data collection:**
   - Need at least 2-3 measurements
   - Check interval setting

2. **Verify monitoring is running:**
   ```python
   print(tester.active_tests)
   # Should show active threads
   ```

3. **Check for exceptions:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Platform-Specific Issues

### macOS: "Operation not permitted" even with sudo

**Solution:**

macOS Catalina+ requires explicit permissions:

```bash
# Grant terminal full disk access:
System Preferences → Security & Privacy → Privacy → Full Disk Access
→ Add Terminal/iTerm
```

Or use System Python:
```bash
sudo /usr/bin/python3 main.py
```

### Windows: ping3 not working

**Solution:**

Windows ICMP handling differs. Use alternative:

```bash
pip install ping3 --force-reinstall

# Or switch to TCP-based ping
# See "Alternative (no root)" above
```

### Linux: "Network is unreachable"

**Solutions:**

1. **Check network interface:**
   ```bash
   ip addr show
   # Verify interface is UP
   ```

2. **Check routing:**
   ```bash
   ip route
   # Should have default gateway
   ```

3. **Test connectivity:**
   ```bash
   ping -c 4 8.8.8.8
   ```

## Debugging Tips

### Enable debug logging

```python
# At top of main.py or web_interface.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Test individual components

```bash
# Test latency measurement
python latency_tester.py

# Test map visualization
python map_visualizer.py

# Test graph plotting
python graph_plotter.py
```

### Check thread status

```python
# Add to your code
import threading
print("Active threads:", threading.active_count())
for thread in threading.enumerate():
    print(f"  - {thread.name}: {thread.is_alive()}")
```

### Monitor network traffic

```bash
# macOS/Linux
sudo tcpdump -i any icmp

# Count ICMP packets
sudo tcpdump -i any icmp -c 20
```

## Getting Help

Still stuck? Here's what to include when asking for help:

1. **Python version:**
   ```bash
   python --version
   ```

2. **OS and version:**
   ```bash
   uname -a  # macOS/Linux
   systeminfo  # Windows
   ```

3. **Installed packages:**
   ```bash
   pip list | grep -E "ping3|folium|matplotlib|flask"
   ```

4. **Full error message:**
   - Copy complete traceback
   - Include command you ran

5. **What you tried:**
   - List solutions attempted
   - Results of each attempt

## Known Limitations

1. **ICMP may be blocked** by corporate firewalls
2. **Requires root** for raw socket access
3. **Geographic accuracy** depends on endpoint locations
4. **Not suitable for** high-frequency monitoring (< 1s interval)
5. **Web interface** has no authentication (dev only)

## Workarounds

### Use without root (HTTP ping)

Replace ICMP with HTTP requests:

```python
import requests
import time

def http_ping(url, timeout=2):
    start = time.time()
    try:
        requests.head(url, timeout=timeout)
        return (time.time() - start) * 1000
    except:
        return None

# Use: http_ping('http://google.com')
```

### Remote monitoring

Run on VPS/cloud instance with public IP:
- Deploy to AWS/GCP/Azure
- Access via public URL
- Add nginx + SSL
- Enable authentication

### Persistent data

Add database storage:

```python
import sqlite3

# Store measurements
conn = sqlite3.connect('latency.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE measurements (
        timestamp TEXT,
        endpoint TEXT,
        latency REAL
    )
''')
```

---

If you found a solution not listed here, please contribute to this guide!
