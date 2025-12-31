"""
Map visualization module for displaying latency connections on a world map.
"""
import folium
from folium import plugins
import numpy as np
from typing import List, Tuple, Dict, Optional
import json


class LatencyMapVisualizer:
    """Creates and manages the world map visualization with latency overlays."""

    def __init__(self, center: Tuple[float, float] = (20, 0), zoom_start: int = 2):
        """
        Initialize the map visualizer.

        Args:
            center: (latitude, longitude) for map center
            zoom_start: Initial zoom level
        """
        self.center = center
        self.zoom_start = zoom_start
        self.endpoints: Dict[str, Dict] = {}
        self.connections: List[Dict] = []

    def create_map(self) -> folium.Map:
        """Create a new folium map with wide atlas view."""
        m = folium.Map(
            location=self.center,
            zoom_start=self.zoom_start,
            tiles='CartoDB positron',
            width='100%',
            height='100%'
        )
        return m

    def add_endpoint(self, endpoint_id: str, name: str, lat: float, lon: float,
                     ip: str, is_source: bool = False):
        """
        Add an endpoint to the map.

        Args:
            endpoint_id: Unique identifier
            name: Display name
            lat: Latitude
            lon: Longitude
            ip: IP address
            is_source: Whether this is a source endpoint
        """
        self.endpoints[endpoint_id] = {
            'name': name,
            'lat': lat,
            'lon': lon,
            'ip': ip,
            'is_source': is_source
        }

    def add_connection(self, source_id: str, target_id: str, latency: Optional[float]):
        """
        Add a connection between two endpoints.

        Args:
            source_id: Source endpoint ID
            target_id: Target endpoint ID
            latency: Latency in milliseconds (None if connection failed)
        """
        if source_id not in self.endpoints or target_id not in self.endpoints:
            return

        self.connections.append({
            'source': source_id,
            'target': target_id,
            'latency': latency
        })

    def _get_color_for_latency(self, latency: Optional[float]) -> str:
        """
        Get color based on latency value.

        Args:
            latency: Latency in milliseconds

        Returns:
            Hex color string
        """
        if latency is None:
            return '#808080'  # Gray for failed connections

        # Color gradient from green (fast) to red (slow)
        if latency < 50:
            return '#00ff00'  # Green
        elif latency < 100:
            return '#7fff00'  # Yellow-green
        elif latency < 150:
            return '#ffff00'  # Yellow
        elif latency < 200:
            return '#ff7f00'  # Orange
        else:
            return '#ff0000'  # Red

    def _get_opacity_for_latency(self, latency: Optional[float]) -> float:
        """Get opacity based on latency (lower latency = more visible)."""
        if latency is None:
            return 0.3
        # Map latency to opacity (0.3 to 0.9)
        return min(0.9, max(0.3, 0.9 - (latency / 500)))

    def _create_arc_coordinates(self, start: Tuple[float, float],
                                end: Tuple[float, float],
                                num_points: int = 100) -> List[Tuple[float, float]]:
        """
        Create arc coordinates for a great circle path with elevation.

        Args:
            start: (lat, lon) start point
            end: (lat, lon) end point
            num_points: Number of points in the arc

        Returns:
            List of (lat, lon) coordinates
        """
        lat1, lon1 = start
        lat2, lon2 = end

        # Calculate the great circle path
        points = []
        for i in range(num_points + 1):
            fraction = i / num_points

            # Linear interpolation with sine curve for height
            lat = lat1 + (lat2 - lat1) * fraction
            lon = lon1 + (lon2 - lon1) * fraction

            # Add elevation effect (arc upward)
            height = np.sin(fraction * np.pi) * 15  # Max 15 degrees elevation
            lat += height

            points.append((lat, lon))

        return points

    def render_map(self, output_path: str = 'latency_map.html'):
        """
        Render the complete map with all endpoints and connections.

        Args:
            output_path: Path to save the HTML file
        """
        m = self.create_map()

        # Draw connections first (so they appear under markers)
        for conn in self.connections:
            source = self.endpoints[conn['source']]
            target = self.endpoints[conn['target']]
            latency = conn['latency']

            color = self._get_color_for_latency(latency)
            opacity = self._get_opacity_for_latency(latency)

            # Create arc path
            arc_points = self._create_arc_coordinates(
                (source['lat'], source['lon']),
                (target['lat'], target['lon'])
            )

            # Draw the arc
            folium.PolyLine(
                arc_points,
                color=color,
                weight=3,
                opacity=opacity,
                popup=f"{source['name']} → {target['name']}<br>Latency: {latency:.2f} ms" if latency else f"{source['name']} → {target['name']}<br>Connection failed"
            ).add_to(m)

            # Add animated marker along the path
            plugins.AntPath(
                arc_points,
                color=color,
                weight=2,
                opacity=opacity * 0.6,
                delay=1000,
                dash_array=[10, 20]
            ).add_to(m)

        # Draw endpoint markers
        for endpoint_id, endpoint in self.endpoints.items():
            color = 'red' if endpoint['is_source'] else 'blue'
            icon = 'play' if endpoint['is_source'] else 'info-sign'

            folium.Marker(
                location=[endpoint['lat'], endpoint['lon']],
                popup=f"<b>{endpoint['name']}</b><br>IP: {endpoint['ip']}<br>Type: {'Source' if endpoint['is_source'] else 'Target'}",
                tooltip=endpoint['name'],
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)

        # Add mouse position plugin
        plugins.MousePosition().add_to(m)

        # Add fullscreen option
        plugins.Fullscreen().add_to(m)

        # Save map
        m.save(output_path)
        print(f"Map saved to {output_path}")

        return m

    def clear_connections(self):
        """Clear all connections while keeping endpoints."""
        self.connections = []

    def clear_all(self):
        """Clear all endpoints and connections."""
        self.endpoints = {}
        self.connections = []


# Predefined endpoint locations for common servers
COMMON_ENDPOINTS = {
    'us_east': {'name': 'US East (Virginia)', 'lat': 37.5, 'lon': -77.5, 'ip': '54.239.28.85'},
    'us_west': {'name': 'US West (California)', 'lat': 37.4, 'lon': -121.9, 'ip': '13.56.63.251'},
    'europe': {'name': 'Europe (Ireland)', 'lat': 53.3, 'lon': -6.3, 'ip': '52.17.0.0'},
    'asia_pacific': {'name': 'Asia Pacific (Singapore)', 'lat': 1.3, 'lon': 103.8, 'ip': '52.77.0.0'},
    'south_america': {'name': 'South America (São Paulo)', 'lat': -23.5, 'lon': -46.6, 'ip': '52.67.0.0'},
    'australia': {'name': 'Australia (Sydney)', 'lat': -33.9, 'lon': 151.2, 'ip': '13.54.0.0'},
    'google_dns': {'name': 'Google DNS', 'lat': 37.4, 'lon': -122.1, 'ip': '8.8.8.8'},
    'cloudflare_dns': {'name': 'Cloudflare DNS', 'lat': 37.8, 'lon': -122.4, 'ip': '1.1.1.1'},
}


if __name__ == "__main__":
    # Demo visualization
    viz = LatencyMapVisualizer()

    # Add source
    viz.add_endpoint('source', 'Your Location', 37.7, -122.4, '192.168.1.1', is_source=True)

    # Add some targets
    viz.add_endpoint('london', 'London', 51.5, -0.1, '8.8.8.8')
    viz.add_endpoint('tokyo', 'Tokyo', 35.7, 139.7, '8.8.4.4')
    viz.add_endpoint('sydney', 'Sydney', -33.9, 151.2, '1.1.1.1')

    # Add connections with sample latencies
    viz.add_connection('source', 'london', 85.3)
    viz.add_connection('source', 'tokyo', 142.7)
    viz.add_connection('source', 'sydney', 178.2)

    # Render
    viz.render_map('demo_map.html')
    print("Demo map created!")
