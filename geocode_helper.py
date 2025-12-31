#!/usr/bin/env python3
"""
Geocoding Helper - Convert city names to latitude/longitude coordinates.

Usage:
    python3 geocode_helper.py "San Francisco"
    python3 geocode_helper.py "Tokyo, Japan"
    python3 geocode_helper.py --interactive
"""

import sys
import argparse
try:
    import urllib.request
    import urllib.parse
    import json
except ImportError:
    print("Error: Required modules not available")
    sys.exit(1)


def geocode_nominatim(location_name):
    """
    Geocode using OpenStreetMap Nominatim (free, no API key required).

    Args:
        location_name: City name or address

    Returns:
        dict with 'lat', 'lon', 'display_name' or None if not found
    """
    try:
        # URL encode the location name
        encoded_location = urllib.parse.quote(location_name)

        # Nominatim API endpoint
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"

        # Add user agent (required by Nominatim)
        headers = {'User-Agent': 'LatencyMapper/1.0'}

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode())

            if data and len(data) > 0:
                result = data[0]
                return {
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'display_name': result['display_name']
                }
            else:
                return None

    except Exception as e:
        print(f"Error geocoding: {e}", file=sys.stderr)
        return None


def geocode_ipapi(location_name):
    """
    Fallback geocoding using ip-api.com (free, no API key).
    Less accurate but works for major cities.
    """
    try:
        encoded_location = urllib.parse.quote(location_name)
        url = f"http://api.ipapi.com/check?access_key=free&fields=city,country_name,latitude,longitude"

        # This is a simplified version - would need city lookup database
        # For now, use Nominatim as primary
        return None

    except Exception as e:
        return None


def format_coordinates(result):
    """Format the geocoding result for display."""
    if not result:
        return None

    return {
        'location': result['display_name'],
        'lat': round(result['lat'], 4),
        'lon': round(result['lon'], 4)
    }


def interactive_mode():
    """Interactive mode for geocoding multiple locations."""
    print("=" * 60)
    print("Geocoding Helper - Interactive Mode")
    print("=" * 60)
    print("\nEnter location names (city, address, etc.)")
    print("Type 'quit' or 'exit' to stop\n")

    while True:
        try:
            location = input("Location: ").strip()

            if location.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not location:
                continue

            print(f"Searching for '{location}'...")
            result = geocode_nominatim(location)

            if result:
                formatted = format_coordinates(result)
                print(f"\n✓ Found: {formatted['location']}")
                print(f"  Latitude:  {formatted['lat']}")
                print(f"  Longitude: {formatted['lon']}")
                print(f"\n  Use in web interface:")
                print(f"    Lat: {formatted['lat']}")
                print(f"    Lon: {formatted['lon']}\n")
            else:
                print(f"✗ Location not found. Try being more specific.\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def batch_geocode(locations):
    """Geocode a list of locations."""
    results = []

    for location in locations:
        print(f"Geocoding: {location}...", end=" ")
        result = geocode_nominatim(location)

        if result:
            formatted = format_coordinates(result)
            results.append(formatted)
            print(f"✓ ({formatted['lat']}, {formatted['lon']})")
        else:
            results.append(None)
            print("✗ Not found")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Convert city names to latitude/longitude coordinates',
        epilog='Example: python3 geocode_helper.py "San Francisco, CA"'
    )

    parser.add_argument('location', nargs='?', help='Location to geocode (city, address, etc.)')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive mode for multiple locations')
    parser.add_argument('-b', '--batch', nargs='+',
                       help='Batch geocode multiple locations')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Output in JSON format')

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        interactive_mode()
        return

    # Batch mode
    if args.batch:
        results = batch_geocode(args.batch)

        if args.json:
            print(json.dumps(results, indent=2))
        return

    # Single location mode
    if args.location:
        result = geocode_nominatim(args.location)

        if result:
            formatted = format_coordinates(result)

            if args.json:
                print(json.dumps(formatted, indent=2))
            else:
                print("\n" + "=" * 60)
                print(f"Location: {formatted['location']}")
                print("=" * 60)
                print(f"Latitude:  {formatted['lat']}")
                print(f"Longitude: {formatted['lon']}")
                print("\nCopy these values to the web interface:")
                print(f"  Lat: {formatted['lat']}")
                print(f"  Lon: {formatted['lon']}")
                print("=" * 60 + "\n")
        else:
            print(f"\n✗ Could not find location: {args.location}")
            print("Try being more specific, e.g., 'Paris, France' instead of just 'Paris'\n")
            sys.exit(1)
    else:
        # No arguments - show help
        parser.print_help()
        print("\nExamples:")
        print("  python3 geocode_helper.py 'Tokyo'")
        print("  python3 geocode_helper.py 'London, UK'")
        print("  python3 geocode_helper.py --interactive")
        print("  python3 geocode_helper.py --batch 'Paris' 'Berlin' 'Rome'")


if __name__ == "__main__":
    main()
