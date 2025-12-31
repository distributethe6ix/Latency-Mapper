"""
Web interface for interactive endpoint selection and real-time updates.
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import threading
import time
from typing import Dict, List
from latency_tester import LatencyTester
from map_visualizer import LatencyMapVisualizer, COMMON_ENDPOINTS


app = Flask(__name__)
CORS(app)

# Global instances
tester = LatencyTester(max_history=200)
visualizer = LatencyMapVisualizer()

# Track active endpoints
active_endpoints: Dict[str, Dict] = {}
source_endpoint: Dict = None


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/endpoints/common', methods=['GET'])
def get_common_endpoints():
    """Get list of predefined common endpoints."""
    return jsonify(COMMON_ENDPOINTS)


@app.route('/api/location/detect', methods=['GET'])
def detect_location():
    """Auto-detect user's location based on IP."""
    try:
        import urllib.request
        import json as json_module

        url = "https://ipapi.co/json/"
        headers = {'User-Agent': 'LatencyMapper/1.0'}
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json_module.loads(response.read().decode())

            return jsonify({
                'success': True,
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name'),
                'lat': float(data.get('latitude', 0)),
                'lon': float(data.get('longitude', 0)),
                'ip': data.get('ip')
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/location/geocode', methods=['POST'])
def geocode_location():
    """Geocode a location name to coordinates."""
    try:
        import urllib.request
        import urllib.parse
        import json as json_module

        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        location_name = data.get('location', '').strip()

        if not location_name:
            return jsonify({'success': False, 'error': 'No location provided'}), 400

        print(f"Geocoding request for: {location_name}")

        # Use Nominatim for geocoding
        encoded = urllib.parse.quote(location_name)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
        headers = {'User-Agent': 'LatencyMapper/1.0'}
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            results = json_module.loads(response.read().decode())

            if results and len(results) > 0:
                result = results[0]
                print(f"Geocoding success: {result['display_name']}")
                return jsonify({
                    'success': True,
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'display_name': result['display_name']
                })
            else:
                print(f"Geocoding failed: No results for '{location_name}'")
                return jsonify({'success': False, 'error': 'Location not found'}), 404

    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        print(f"Geocoding HTTP error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500
    except urllib.error.URLError as e:
        error_msg = f"URL Error: {e.reason}"
        print(f"Geocoding URL error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500
    except Exception as e:
        error_msg = str(e)
        print(f"Geocoding exception: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/source', methods=['POST'])
def set_source():
    """Set the source endpoint."""
    global source_endpoint

    data = request.json
    source_endpoint = {
        'id': 'source',
        'name': data['name'],
        'lat': float(data['lat']),
        'lon': float(data['lon']),
        'ip': data['ip']
    }

    visualizer.add_endpoint(
        'source',
        source_endpoint['name'],
        source_endpoint['lat'],
        source_endpoint['lon'],
        source_endpoint['ip'],
        is_source=True
    )

    return jsonify({'status': 'success', 'source': source_endpoint})


@app.route('/api/endpoints/add', methods=['POST'])
def add_endpoint():
    """Add a target endpoint and start monitoring."""
    global active_endpoints

    data = request.json
    endpoint_id = f"endpoint_{len(active_endpoints)}"

    endpoint = {
        'id': endpoint_id,
        'name': data['name'],
        'lat': float(data['lat']),
        'lon': float(data['lon']),
        'ip': data['ip']
    }

    active_endpoints[endpoint_id] = endpoint

    # Add to visualizer
    visualizer.add_endpoint(
        endpoint_id,
        endpoint['name'],
        endpoint['lat'],
        endpoint['lon'],
        endpoint['ip'],
        is_source=False
    )

    # Start monitoring
    tester.start_monitoring(endpoint_id, endpoint['ip'], interval=2.0)

    return jsonify({'status': 'success', 'endpoint': endpoint})


@app.route('/api/endpoints/remove', methods=['POST'])
def remove_endpoint():
    """Remove an endpoint and stop monitoring."""
    global active_endpoints

    data = request.json
    endpoint_id = data['id']

    if endpoint_id in active_endpoints:
        # Stop monitoring
        tester.stop_monitoring(endpoint_id)

        # Remove from active endpoints
        del active_endpoints[endpoint_id]

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404


@app.route('/api/endpoints/list', methods=['GET'])
def list_endpoints():
    """Get list of all active endpoints."""
    return jsonify({
        'source': source_endpoint,
        'endpoints': list(active_endpoints.values())
    })


@app.route('/api/latency/current', methods=['GET'])
def get_current_latency():
    """Get current latency for all endpoints."""
    result = {}

    for endpoint_id in active_endpoints.keys():
        latency = tester.get_latest_latency(endpoint_id)
        stats = tester.get_statistics(endpoint_id)

        result[endpoint_id] = {
            'current': latency,
            'stats': stats
        }

    return jsonify(result)


@app.route('/api/latency/history', methods=['GET'])
def get_latency_history():
    """Get historical latency data for all endpoints."""
    endpoint_id = request.args.get('endpoint_id')

    if endpoint_id:
        # Single endpoint
        history = tester.get_history(endpoint_id)
        # Convert datetime to ISO format for JSON
        formatted_history = [
            {
                'timestamp': m['timestamp'].isoformat(),
                'latency': m['latency'],
                'success': m['success']
            }
            for m in history
        ]
        return jsonify({endpoint_id: formatted_history})
    else:
        # All endpoints
        result = {}
        for ep_id in active_endpoints.keys():
            history = tester.get_history(ep_id)
            formatted_history = [
                {
                    'timestamp': m['timestamp'].isoformat(),
                    'latency': m['latency'],
                    'success': m['success']
                }
                for m in history
            ]
            result[ep_id] = formatted_history
        return jsonify(result)


@app.route('/api/map/generate', methods=['POST'])
def generate_map():
    """Generate and save the current map visualization."""
    # Clear old connections
    visualizer.clear_connections()

    # Add current connections with latest latency
    for endpoint_id in active_endpoints.keys():
        latency = tester.get_latest_latency(endpoint_id)
        if source_endpoint:
            visualizer.add_connection('source', endpoint_id, latency)

    # Render map
    output_path = 'static/current_map.html'
    visualizer.render_map(output_path)

    return jsonify({'status': 'success', 'path': output_path})


@app.route('/api/map/view')
def view_map():
    """View the generated map."""
    try:
        with open('static/current_map.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Map not generated yet. Please add endpoints and generate the map first.", 404


def auto_update_map():
    """Background thread to auto-update the map."""
    while True:
        time.sleep(10)  # Update every 10 seconds
        if source_endpoint and active_endpoints:
            visualizer.clear_connections()
            for endpoint_id in active_endpoints.keys():
                latency = tester.get_latest_latency(endpoint_id)
                visualizer.add_connection('source', endpoint_id, latency)
            visualizer.render_map('static/current_map.html')


# Start auto-update thread
update_thread = threading.Thread(target=auto_update_map, daemon=True)
update_thread.start()


if __name__ == '__main__':
    import os
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Latency Mapper Web Interface')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()

    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    print("=" * 60)
    print("Latency Mapper Web Interface")
    print("=" * 60)
    print(f"\nStarting server at http://localhost:{args.port}")
    print("\nNote: You may need to run this with sudo to use ICMP ping")
    print(f"      sudo python3 web_interface.py --port {args.port}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    try:
        app.run(debug=True, host=args.host, port=args.port, use_reloader=False)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n❌ ERROR: Port {args.port} is already in use!")
            print("\nSolutions:")
            print(f"  1. Use a different port: sudo python3 web_interface.py --port 5001")
            print(f"  2. Find and kill the process using port {args.port}:")
            print(f"     lsof -ti:{args.port} | xargs kill -9")
            print(f"  3. On macOS: lsof -i :{args.port}")
            print(f"     On Linux: sudo netstat -tlnp | grep {args.port}")
        else:
            raise
