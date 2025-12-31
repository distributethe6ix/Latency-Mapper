"""
Historical latency graph plotting module.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np


class LatencyGraphPlotter:
    """Creates historical latency graphs using matplotlib."""

    def __init__(self, figsize: tuple = (12, 6)):
        """
        Initialize the graph plotter.

        Args:
            figsize: Figure size (width, height) in inches
        """
        self.figsize = figsize
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_single_endpoint(self, history: List[Dict], endpoint_name: str,
                            output_path: Optional[str] = None) -> plt.Figure:
        """
        Plot latency history for a single endpoint.

        Args:
            history: List of measurement dicts with 'timestamp', 'latency', 'success'
            endpoint_name: Name of the endpoint for the title
            output_path: Optional path to save the figure

        Returns:
            matplotlib Figure object
        """
        if not history:
            print("No data to plot")
            return None

        fig, ax = plt.subplots(figsize=self.figsize)

        # Extract data
        timestamps = [m['timestamp'] for m in history]
        latencies = [m['latency'] if m['success'] else None for m in history]

        # Plot successful pings
        success_times = [t for t, l in zip(timestamps, latencies) if l is not None]
        success_latencies = [l for l in latencies if l is not None]

        if success_latencies:
            ax.plot(success_times, success_latencies, marker='o', linestyle='-',
                   color='#2E86AB', linewidth=2, markersize=4, label='Latency')

            # Add average line
            avg_latency = np.mean(success_latencies)
            ax.axhline(y=avg_latency, color='#A23B72', linestyle='--',
                      linewidth=2, label=f'Average: {avg_latency:.2f} ms')

        # Mark failed pings
        failed_times = [t for t, l in zip(timestamps, latencies) if l is None]
        if failed_times:
            failed_y = [max(success_latencies) * 1.1 if success_latencies else 100] * len(failed_times)
            ax.scatter(failed_times, failed_y, color='red', marker='x',
                      s=100, label='Failed', zorder=5)

        # Formatting
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
        ax.set_title(f'Latency History: {endpoint_name}', fontsize=14, fontweight='bold')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45, ha='right')

        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Graph saved to {output_path}")

        return fig

    def plot_multiple_endpoints(self, endpoint_data: Dict[str, List[Dict]],
                               output_path: Optional[str] = None) -> plt.Figure:
        """
        Plot latency comparison for multiple endpoints.

        Args:
            endpoint_data: Dict mapping endpoint names to their history lists
            output_path: Optional path to save the figure

        Returns:
            matplotlib Figure object
        """
        if not endpoint_data:
            print("No data to plot")
            return None

        fig, ax = plt.subplots(figsize=self.figsize)

        colors = plt.cm.tab10(np.linspace(0, 1, len(endpoint_data)))

        for (endpoint_name, history), color in zip(endpoint_data.items(), colors):
            if not history:
                continue

            # Extract successful measurements
            timestamps = [m['timestamp'] for m in history if m['success']]
            latencies = [m['latency'] for m in history if m['success']]

            if timestamps and latencies:
                ax.plot(timestamps, latencies, marker='o', linestyle='-',
                       color=color, linewidth=2, markersize=3,
                       label=f"{endpoint_name} (avg: {np.mean(latencies):.1f}ms)")

        # Formatting
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Latency Comparison: Multiple Endpoints', fontsize=14, fontweight='bold')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45, ha='right')

        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Graph saved to {output_path}")

        return fig

    def plot_heatmap(self, endpoint_data: Dict[str, List[Dict]],
                    output_path: Optional[str] = None) -> plt.Figure:
        """
        Plot latency heatmap over time for multiple endpoints.

        Args:
            endpoint_data: Dict mapping endpoint names to their history lists
            output_path: Optional path to save the figure

        Returns:
            matplotlib Figure object
        """
        if not endpoint_data:
            print("No data to plot")
            return None

        # Prepare data matrix
        endpoint_names = list(endpoint_data.keys())
        max_len = max(len(hist) for hist in endpoint_data.values())

        latency_matrix = []
        for name in endpoint_names:
            history = endpoint_data[name]
            latencies = [m['latency'] if m['success'] else np.nan for m in history]
            # Pad to max length
            latencies += [np.nan] * (max_len - len(latencies))
            latency_matrix.append(latencies)

        latency_matrix = np.array(latency_matrix)

        fig, ax = plt.subplots(figsize=(14, max(6, len(endpoint_names) * 0.5)))

        im = ax.imshow(latency_matrix, aspect='auto', cmap='RdYlGn_r',
                      interpolation='nearest', vmin=0, vmax=300)

        # Set ticks
        ax.set_yticks(np.arange(len(endpoint_names)))
        ax.set_yticklabels(endpoint_names)
        ax.set_xlabel('Measurement #', fontsize=12, fontweight='bold')
        ax.set_title('Latency Heatmap Over Time', fontsize=14, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Latency (ms)', fontsize=12)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Heatmap saved to {output_path}")

        return fig

    def plot_statistics_bars(self, endpoint_stats: Dict[str, Dict],
                            output_path: Optional[str] = None) -> plt.Figure:
        """
        Plot bar chart of latency statistics for multiple endpoints.

        Args:
            endpoint_stats: Dict mapping endpoint names to their statistics
            output_path: Optional path to save the figure

        Returns:
            matplotlib Figure object
        """
        if not endpoint_stats:
            print("No data to plot")
            return None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.figsize[0], self.figsize[1] * 1.2))

        endpoint_names = list(endpoint_stats.keys())
        avg_latencies = [stats['avg_latency'] or 0 for stats in endpoint_stats.values()]
        min_latencies = [stats['min_latency'] or 0 for stats in endpoint_stats.values()]
        max_latencies = [stats['max_latency'] or 0 for stats in endpoint_stats.values()]
        success_rates = [stats['success_rate'] * 100 for stats in endpoint_stats.values()]

        x = np.arange(len(endpoint_names))
        width = 0.25

        # Latency bars
        bars1 = ax1.bar(x - width, min_latencies, width, label='Min', color='#06A77D')
        bars2 = ax1.bar(x, avg_latencies, width, label='Avg', color='#2E86AB')
        bars3 = ax1.bar(x + width, max_latencies, width, label='Max', color='#A23B72')

        ax1.set_xlabel('Endpoint', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
        ax1.set_title('Latency Statistics by Endpoint', fontsize=13, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(endpoint_names, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # Success rate bars
        bars4 = ax2.bar(x, success_rates, color='#F18F01')
        ax2.axhline(y=100, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Endpoint', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Success Rate (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Connection Success Rate by Endpoint', fontsize=13, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(endpoint_names, rotation=45, ha='right')
        ax2.set_ylim([0, 105])
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Statistics chart saved to {output_path}")

        return fig


if __name__ == "__main__":
    # Demo the plotter
    from datetime import timedelta

    # Generate sample data
    now = datetime.now()
    history = []
    for i in range(50):
        history.append({
            'timestamp': now + timedelta(seconds=i),
            'latency': 50 + np.random.normal(0, 10) + i * 0.5,  # Gradually increasing latency
            'success': np.random.random() > 0.05  # 95% success rate
        })

    plotter = LatencyGraphPlotter()

    # Plot single endpoint
    plotter.plot_single_endpoint(history, "Test Server", "demo_graph.png")

    print("Demo graph created!")
