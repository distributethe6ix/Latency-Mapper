#!/usr/bin/env python3
"""
Location Detector - Auto-detect your current location based on IP address.

Usage:
    python3 location_detector.py
    python3 location_detector.py --json
    python3 location_detector.py --verbose
"""

import sys
import argparse
try:
    import urllib.request
    import json
except ImportError:
    print("Error: Required modules not available")
    sys.exit(1)


def detect_location_ipapi():
    """
    Detect location using ipapi.co (free, no API key required).

    Returns:
        dict with location info or None if failed
    """
    try:
        url = "https://ipapi.co/json/"
        headers = {'User-Agent': 'LatencyMapper/1.0'}

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode())

            return {
                'ip': data.get('ip'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name'),
                'country_code': data.get('country_code'),
                'lat': float(data.get('latitude', 0)),
                'lon': float(data.get('longitude', 0)),
                'timezone': data.get('timezone'),
                'isp': data.get('org'),
                'source': 'ipapi.co'
            }

    except Exception as e:
        print(f"ipapi.co failed: {e}", file=sys.stderr)
        return None


def detect_location_ipinfo():
    """
    Fallback using ipinfo.io (free tier available).

    Returns:
        dict with location info or None if failed
    """
    try:
        url = "https://ipinfo.io/json"
        headers = {'User-Agent': 'LatencyMapper/1.0'}

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode())

            # Parse "lat,lon" format
            loc_parts = data.get('loc', '0,0').split(',')

            return {
                'ip': data.get('ip'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country'),
                'country_code': data.get('country'),
                'lat': float(loc_parts[0]) if len(loc_parts) > 0 else 0,
                'lon': float(loc_parts[1]) if len(loc_parts) > 1 else 0,
                'timezone': data.get('timezone'),
                'isp': data.get('org'),
                'source': 'ipinfo.io'
            }

    except Exception as e:
        print(f"ipinfo.io failed: {e}", file=sys.stderr)
        return None


def detect_location_ipgeolocation():
    """
    Another fallback using ip-api.com (completely free, no key needed).

    Returns:
        dict with location info or None if failed
    """
    try:
        url = "http://ip-api.com/json/"
        headers = {'User-Agent': 'LatencyMapper/1.0'}

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode())

            if data.get('status') == 'success':
                return {
                    'ip': data.get('query'),
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'lat': float(data.get('lat', 0)),
                    'lon': float(data.get('lon', 0)),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'source': 'ip-api.com'
                }
            else:
                return None

    except Exception as e:
        print(f"ip-api.com failed: {e}", file=sys.stderr)
        return None


def detect_location(verbose=False):
    """
    Try multiple services to detect location.

    Args:
        verbose: Print additional debug info

    Returns:
        dict with location info or None if all failed
    """
    services = [
        ('ipapi.co', detect_location_ipapi),
        ('ipinfo.io', detect_location_ipinfo),
        ('ip-api.com', detect_location_ipgeolocation)
    ]

    for service_name, detect_func in services:
        if verbose:
            print(f"Trying {service_name}...", file=sys.stderr)

        result = detect_func()

        if result and result.get('lat') != 0 and result.get('lon') != 0:
            if verbose:
                print(f"✓ Success with {service_name}", file=sys.stderr)
            return result

    return None


def format_location_display(location):
    """Format location data for display."""
    if not location:
        return "Location detection failed"

    output = []
    output.append("=" * 60)
    output.append("YOUR CURRENT LOCATION")
    output.append("=" * 60)
    output.append(f"IP Address:    {location['ip']}")
    output.append(f"City:          {location['city']}, {location['region']}")
    output.append(f"Country:       {location['country']} ({location['country_code']})")
    output.append(f"Coordinates:   {location['lat']}, {location['lon']}")
    output.append(f"Timezone:      {location['timezone']}")
    output.append(f"ISP:           {location['isp']}")
    output.append(f"Data source:   {location['source']}")
    output.append("=" * 60)
    output.append("\nUse these values in the web interface:")
    output.append(f"  Name:      {location['city']}, {location['country_code']}")
    output.append(f"  Latitude:  {location['lat']}")
    output.append(f"  Longitude: {location['lon']}")
    output.append(f"  IP:        {location['ip']}")
    output.append("=" * 60)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Auto-detect your current location based on IP address',
        epilog='Note: Location is approximate based on your public IP address'
    )

    parser.add_argument('-j', '--json', action='store_true',
                       help='Output in JSON format')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output with debug info')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Only output coordinates (lat,lon)')

    args = parser.parse_args()

    # Detect location
    if args.verbose and not args.quiet:
        print("Detecting your location...\n", file=sys.stderr)

    location = detect_location(verbose=args.verbose)

    if not location:
        print("\n✗ Could not detect location. Possible reasons:", file=sys.stderr)
        print("  - No internet connection", file=sys.stderr)
        print("  - Firewall blocking requests", file=sys.stderr)
        print("  - All geolocation services are down", file=sys.stderr)
        print("\nTry manually getting your coordinates from:", file=sys.stderr)
        print("  - https://www.google.com/maps (right-click your location)", file=sys.stderr)
        print("  - https://www.latlong.net/", file=sys.stderr)
        sys.exit(1)

    # Output based on format
    if args.json:
        print(json.dumps(location, indent=2))
    elif args.quiet:
        print(f"{location['lat']},{location['lon']}")
    else:
        print("\n" + format_location_display(location) + "\n")


if __name__ == "__main__":
    main()
