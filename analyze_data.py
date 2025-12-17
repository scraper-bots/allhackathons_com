import json
from collections import Counter
from datetime import datetime
import re


def load_hackathons(filename='remote_hackathons.json'):
    """Load hackathons from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_statistics(hackathons):
    """Get statistics about the hackathons"""
    stats = {
        'total': len(hackathons),
        'status': Counter(),
        'location_type': Counter(),
        'themes': Counter(),
        'with_prizes': 0,
        'with_organizer': 0,
        'with_website': 0,
    }

    for h in hackathons:
        # Count by status
        if 'status' in h:
            stats['status'][h['status']] += 1

        # Count by location type
        if 'location_type' in h:
            stats['location_type'][h['location_type']] += 1

        # Count themes
        if 'themes' in h:
            for theme in h['themes']:
                stats['themes'][theme] += 1

        # Count optional fields
        if h.get('prizes') and h['prizes'] != '$0':
            stats['with_prizes'] += 1

        if h.get('organizer'):
            stats['with_organizer'] += 1

        if h.get('website'):
            stats['with_website'] += 1

    return stats


def filter_hackathons(hackathons, **filters):
    """
    Filter hackathons by various criteria

    Args:
        status: 'Upcoming', 'Open', 'Ended'
        location_type: 'ONLINE', 'IN-PERSON'
        theme: specific theme to filter by
        has_prizes: True/False
        has_website: True/False

    Returns:
        Filtered list of hackathons
    """
    filtered = hackathons

    if 'status' in filters:
        filtered = [h for h in filtered if h.get('status') == filters['status']]

    if 'location_type' in filters:
        filtered = [h for h in filtered if h.get('location_type') == filters['location_type']]

    if 'theme' in filters:
        filtered = [h for h in filtered if filters['theme'] in h.get('themes', [])]

    if 'has_prizes' in filters and filters['has_prizes']:
        filtered = [h for h in filtered if h.get('prizes') and h['prizes'] != '$0']

    if 'has_website' in filters and filters['has_website']:
        filtered = [h for h in filtered if h.get('website')]

    return filtered


def print_statistics(stats):
    """Print statistics in a readable format"""
    print("=" * 60)
    print("HACKATHON DATA STATISTICS")
    print("=" * 60)
    print(f"\nTotal Hackathons: {stats['total']}")

    print("\nBy Status:")
    for status, count in stats['status'].most_common():
        print(f"  {status}: {count}")

    print("\nBy Location Type:")
    for loc_type, count in stats['location_type'].most_common():
        print(f"  {loc_type}: {count}")

    print("\nTop 10 Themes:")
    for theme, count in stats['themes'].most_common(10):
        print(f"  {theme}: {count}")

    print(f"\nHackathons with Prizes: {stats['with_prizes']}")
    print(f"Hackathons with Organizer Info: {stats['with_organizer']}")
    print(f"Hackathons with Website: {stats['with_website']}")


def export_to_csv(hackathons, filename='hackathons.csv'):
    """Export hackathons to CSV format"""
    import csv

    fieldnames = [
        'title', 'status', 'location_type', 'dates', 'location',
        'organizer', 'prizes', 'themes', 'website', 'detail_url'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for h in hackathons:
            # Convert themes list to string
            row = h.copy()
            if 'themes' in row:
                row['themes'] = ', '.join(row['themes'])
            writer.writerow(row)

    print(f"\nData exported to {filename}")


def main():
    """Main function"""
    # Load data
    print("Loading hackathons...")
    hackathons = load_hackathons()

    # Show statistics
    stats = get_statistics(hackathons)
    print_statistics(stats)

    # Example filters
    print("\n" + "=" * 60)
    print("FILTERED RESULTS")
    print("=" * 60)

    # Filter for upcoming online hackathons
    upcoming_online = filter_hackathons(
        hackathons,
        status='Upcoming',
        location_type='ONLINE'
    )
    print(f"\nUpcoming Online Hackathons: {len(upcoming_online)}")
    if upcoming_online:
        print("Sample:")
        for h in upcoming_online[:3]:
            print(f"  - {h['title']} ({h.get('dates', 'N/A')})")

    # Filter for AI-themed hackathons
    ai_hackathons = filter_hackathons(hackathons, theme='ai')
    print(f"\nAI-themed Hackathons: {len(ai_hackathons)}")
    if ai_hackathons:
        print("Sample:")
        for h in ai_hackathons[:3]:
            print(f"  - {h['title']}")

    # Filter for hackathons with prizes
    with_prizes = filter_hackathons(hackathons, has_prizes=True)
    print(f"\nHackathons with Prizes: {len(with_prizes)}")
    if with_prizes:
        print("Sample:")
        for h in with_prizes[:3]:
            print(f"  - {h['title']} - {h.get('prizes', 'N/A')}")

    # Export to CSV
    print("\n" + "=" * 60)
    export_to_csv(hackathons)


if __name__ == "__main__":
    main()
