"""
Latency measurement module for testing network latency between endpoints.
"""
import time
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import deque
import ping3


class LatencyTester:
    """Handles real-time latency measurements using ICMP ping."""

    def __init__(self, max_history: int = 100):
        """
        Initialize the latency tester.

        Args:
            max_history: Maximum number of historical measurements to keep per endpoint
        """
        self.max_history = max_history
        self.measurements: Dict[str, deque] = {}
        self.active_tests: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}

        # Set timeout for ping3
        ping3.EXCEPTIONS = False

    def start_monitoring(self, endpoint_id: str, target_ip: str, interval: float = 1.0):
        """
        Start continuous latency monitoring for an endpoint.

        Args:
            endpoint_id: Unique identifier for this endpoint
            target_ip: IP address or hostname to ping
            interval: Time between pings in seconds
        """
        if endpoint_id in self.active_tests and self.active_tests[endpoint_id].is_alive():
            return  # Already monitoring

        # Initialize storage
        if endpoint_id not in self.measurements:
            self.measurements[endpoint_id] = deque(maxlen=self.max_history)

        # Create stop flag
        stop_flag = threading.Event()
        self.stop_flags[endpoint_id] = stop_flag

        # Start monitoring thread
        thread = threading.Thread(
            target=self._monitor_loop,
            args=(endpoint_id, target_ip, interval, stop_flag),
            daemon=True
        )
        self.active_tests[endpoint_id] = thread
        thread.start()

    def _monitor_loop(self, endpoint_id: str, target_ip: str, interval: float, stop_flag: threading.Event):
        """Internal loop for continuous latency monitoring."""
        while not stop_flag.is_set():
            start_time = time.time()

            # Perform ping
            latency = ping3.ping(target_ip, timeout=2)

            # Store result
            timestamp = datetime.now()
            if latency is not None:
                # Convert to milliseconds
                latency_ms = latency * 1000
                self.measurements[endpoint_id].append({
                    'timestamp': timestamp,
                    'latency': latency_ms,
                    'success': True
                })
            else:
                # Ping failed
                self.measurements[endpoint_id].append({
                    'timestamp': timestamp,
                    'latency': None,
                    'success': False
                })

            # Wait for next interval
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            stop_flag.wait(sleep_time)

    def stop_monitoring(self, endpoint_id: str):
        """Stop monitoring an endpoint."""
        if endpoint_id in self.stop_flags:
            self.stop_flags[endpoint_id].set()
        if endpoint_id in self.active_tests:
            del self.active_tests[endpoint_id]

    def stop_all(self):
        """Stop all active monitoring."""
        for endpoint_id in list(self.stop_flags.keys()):
            self.stop_monitoring(endpoint_id)

    def get_latest_latency(self, endpoint_id: str) -> Optional[float]:
        """Get the most recent latency measurement for an endpoint."""
        if endpoint_id not in self.measurements or len(self.measurements[endpoint_id]) == 0:
            return None

        latest = self.measurements[endpoint_id][-1]
        return latest['latency'] if latest['success'] else None

    def get_history(self, endpoint_id: str) -> List[Dict]:
        """Get all historical measurements for an endpoint."""
        if endpoint_id not in self.measurements:
            return []
        return list(self.measurements[endpoint_id])

    def get_statistics(self, endpoint_id: str) -> Dict:
        """Calculate statistics for an endpoint."""
        history = self.get_history(endpoint_id)
        if not history:
            return {
                'count': 0,
                'success_rate': 0.0,
                'avg_latency': None,
                'min_latency': None,
                'max_latency': None
            }

        successful = [m['latency'] for m in history if m['success']]
        total = len(history)

        return {
            'count': total,
            'success_rate': len(successful) / total if total > 0 else 0.0,
            'avg_latency': sum(successful) / len(successful) if successful else None,
            'min_latency': min(successful) if successful else None,
            'max_latency': max(successful) if successful else None
        }


if __name__ == "__main__":
    # Test the latency tester
    tester = LatencyTester()

    print("Testing latency to Google DNS (8.8.8.8)...")
    tester.start_monitoring("google_dns", "8.8.8.8", interval=1.0)

    try:
        for i in range(10):
            time.sleep(1)
            latency = tester.get_latest_latency("google_dns")
            if latency:
                print(f"Ping {i+1}: {latency:.2f} ms")
            else:
                print(f"Ping {i+1}: Failed")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        tester.stop_all()
        stats = tester.get_statistics("google_dns")
        print(f"\nStatistics:")
        print(f"  Success rate: {stats['success_rate']*100:.1f}%")
        print(f"  Average: {stats['avg_latency']:.2f} ms" if stats['avg_latency'] else "  Average: N/A")
        print(f"  Min: {stats['min_latency']:.2f} ms" if stats['min_latency'] else "  Min: N/A")
        print(f"  Max: {stats['max_latency']:.2f} ms" if stats['max_latency'] else "  Max: N/A")
