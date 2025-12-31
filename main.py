#!/usr/bin/env python3
"""
Latency Mapper - Main Application
Interactive latency visualization tool with real-time monitoring.
"""
import argparse
import sys
import time
from typing import List, Dict
from latency_tester import LatencyTester
from map_visualizer import LatencyMapVisualizer, COMMON_ENDPOINTS
from graph_plotter import LatencyGraphPlotter


class LatencyMapperApp:
    """Main application for latency mapping."""

    def __init__(self):
        self.tester = LatencyTester(max_history=200)
        self.visualizer = LatencyMapVisualizer()
        self.plotter = LatencyGraphPlotter()
        self.endpoints: Dict[str, Dict] = {}
        self.source = None

    def add_source(self, name: str, lat: float, lon: float, ip: str):
        """Set the source endpoint."""
        self.source = {
            'id': 'source',
            'name': name,
            'lat': lat,
            'lon': lon,
            'ip': ip
        }
        self.visualizer.add_endpoint('source', name, lat, lon, ip, is_source=True)
        print(f"✓ Source set: {name} ({lat}, {lon}) - {ip}")

    def add_endpoint(self, name: str, lat: float, lon: float, ip: str):
        """Add a target endpoint."""
        endpoint_id = f"ep_{len(self.endpoints)}"
        self.endpoints[endpoint_id] = {
            'name': name,
            'lat': lat,
            'lon': lon,
            'ip': ip
        }
        self.visualizer.add_endpoint(endpoint_id, name, lat, lon, ip)
        print(f"✓ Endpoint added: {name} ({lat}, {lon}) - {ip}")
        return endpoint_id

    def start_monitoring(self, duration: int = 60, interval: float = 2.0):
        """Start monitoring all endpoints."""
        if not self.source:
            print("Error: No source endpoint set. Use add_source() first.")
            return

        if not self.endpoints:
            print("Error: No target endpoints added. Use add_endpoint() first.")
            return

        print(f"\n{'='*60}")
        print(f"Starting latency monitoring for {duration} seconds...")
        print(f"Ping interval: {interval} seconds")
        print(f"Source: {self.source['name']}")
        print(f"Targets: {', '.join([ep['name'] for ep in self.endpoints.values()])}")
        print(f"{'='*60}\n")

        # Start monitoring all endpoints
        for endpoint_id, endpoint in self.endpoints.items():
            self.tester.start_monitoring(endpoint_id, endpoint['ip'], interval)

        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed

                # Display current status
                sys.stdout.write(f"\r[{elapsed:03d}s / {duration}s] ")

                status_parts = []
                for endpoint_id, endpoint in self.endpoints.items():
                    latency = self.tester.get_latest_latency(endpoint_id)
                    if latency is not None:
                        status_parts.append(f"{endpoint['name']}: {latency:.1f}ms")
                    else:
                        status_parts.append(f"{endpoint['name']}: FAIL")

                sys.stdout.write(" | ".join(status_parts))
                sys.stdout.flush()

                time.sleep(1)

            print("\n\nMonitoring complete!")

        except KeyboardInterrupt:
            print("\n\nMonitoring interrupted by user.")

        finally:
            self.tester.stop_all()

    def generate_visualizations(self, output_prefix: str = "latency"):
        """Generate all visualizations (map and graphs)."""
        print(f"\n{'='*60}")
        print("Generating visualizations...")
        print(f"{'='*60}")

        # Generate map
        self.visualizer.clear_connections()
        for endpoint_id, endpoint in self.endpoints.items():
            latency = self.tester.get_latest_latency(endpoint_id)
            self.visualizer.add_connection('source', endpoint_id, latency)

        map_path = f"{output_prefix}_map.html"
        self.visualizer.render_map(map_path)
        print(f"✓ Map saved: {map_path}")

        # Generate graphs
        endpoint_data = {}
        endpoint_stats = {}

        for endpoint_id, endpoint in self.endpoints.items():
            history = self.tester.get_history(endpoint_id)
            if history:
                endpoint_data[endpoint['name']] = history
                endpoint_stats[endpoint['name']] = self.tester.get_statistics(endpoint_id)

        if endpoint_data:
            # Multiple endpoint comparison
            comparison_path = f"{output_prefix}_comparison.png"
            self.plotter.plot_multiple_endpoints(endpoint_data, comparison_path)
            print(f"✓ Comparison graph saved: {comparison_path}")

            # Statistics bars
            stats_path = f"{output_prefix}_statistics.png"
            self.plotter.plot_statistics_bars(endpoint_stats, stats_path)
            print(f"✓ Statistics chart saved: {stats_path}")

            # Heatmap
            heatmap_path = f"{output_prefix}_heatmap.png"
            self.plotter.plot_heatmap(endpoint_data, heatmap_path)
            print(f"✓ Heatmap saved: {heatmap_path}")

        print(f"{'='*60}\n")

    def print_statistics(self):
        """Print statistics for all endpoints."""
        print(f"\n{'='*60}")
        print("LATENCY STATISTICS")
        print(f"{'='*60}")

        for endpoint_id, endpoint in self.endpoints.items():
            stats = self.tester.get_statistics(endpoint_id)
            print(f"\n{endpoint['name']} ({endpoint['ip']}):")
            print(f"  Measurements: {stats['count']}")
            print(f"  Success rate: {stats['success_rate']*100:.1f}%")

            if stats['avg_latency'] is not None:
                print(f"  Average: {stats['avg_latency']:.2f} ms")
                print(f"  Min: {stats['min_latency']:.2f} ms")
                print(f"  Max: {stats['max_latency']:.2f} ms")
            else:
                print(f"  No successful measurements")

        print(f"\n{'='*60}\n")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Latency Mapper - Visualize network latency on a world map'
    )
    parser.add_argument('--web', action='store_true',
                       help='Start web interface instead of CLI mode')
    parser.add_argument('--duration', type=int, default=60,
                       help='Monitoring duration in seconds (default: 60)')
    parser.add_argument('--interval', type=float, default=2.0,
                       help='Ping interval in seconds (default: 2.0)')
    parser.add_argument('--output', type=str, default='latency',
                       help='Output file prefix (default: latency)')

    args = parser.parse_args()

    if args.web:
        print("Starting web interface...")
        import web_interface
        return

    # CLI mode - run demo
    print("""
╔══════════════════════════════════════════════════════════╗
║           LATENCY MAPPER - Network Latency Tool          ║
╚══════════════════════════════════════════════════════════╝
    """)

    app = LatencyMapperApp()

    # Set up demo configuration
    print("Setting up demo configuration...\n")

    # Source (example: San Francisco)
    app.add_source("San Francisco, CA", 37.7749, -122.4194, "8.8.8.8")

    # Add common endpoints
    print("\nAdding target endpoints:")
    app.add_endpoint("London", 51.5074, -0.1278, "8.8.8.8")
    app.add_endpoint("Tokyo", 35.6762, 139.6503, "8.8.4.4")
    app.add_endpoint("Sydney", -33.8688, 151.2093, "1.1.1.1")
    app.add_endpoint("New York", 40.7128, -74.0060, "1.0.0.1")

    # Start monitoring
    app.start_monitoring(duration=args.duration, interval=args.interval)

    # Print statistics
    app.print_statistics()

    # Generate visualizations
    app.generate_visualizations(output_prefix=args.output)

    print("""
✓ All done! Open the generated HTML file in your browser to view the map.

TIP: For interactive mode with custom endpoints, run:
     python3 main.py --web
     (or: sudo python3 main.py --web for ICMP ping support)

Then open http://localhost:5000 in your browser.
    """)


if __name__ == "__main__":
    main()
