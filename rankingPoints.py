import requests
import json
import os

# Replace with your Blue Alliance API key
API_KEY = "8w7ZQ4zr57LL0SkFqrCRFU2yMPkKvYzCJAaNbNIAppB2lextbcjodNPnXWbLaStt"

def fetch_data(url):
    """Fetch data from a given URL and return the JSON response."""
    headers = {"X-TBA-Auth-Key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def get_nc_events():
    """Fetch all North Carolina district events."""
    url = f"https://www.thebluealliance.com/api/v3/district/2025fnc/events"
    return fetch_data(url)

def get_event_ranking_points(event_key):
    """Fetch ranking points (previously district points) for a given event."""
    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/district_points"
    return fetch_data(url)

def update_nc_data(filename="NC_Data.json"):
    """Update NC_Data.json with total ranking points for each team."""
    # Load NC_Data.json
    try:
        with open(filename, "r") as file:
            nc_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return

    # Fetch all North Carolina district events
    events = get_nc_events()
    if not events:
        print("No events found for North Carolina district.")
        return

    # Dictionary to track total ranking points for each team
    ranking_points = {}

    # Aggregate ranking points across all events
    for event in events:
        event_key = event["key"]
        event_name = event["name"]
        print(f"Processing event: {event_name} ({event_key})")

        # Fetch ranking points for the event
        event_points = get_event_ranking_points(event_key)
        if not event_points or "points" not in event_points:
            print(f"No ranking points found for event {event_name}.")
            continue

        # Update ranking points for each team
        for team_key, points_data in event_points["points"].items():
            ranking_points[team_key] = ranking_points.get(team_key, 0) + points_data.get("total", 0)

    # Update NC_Data.json with total ranking points
    for team in nc_data:
        team_key = team["team_number"]
        team["ranking_points"] = ranking_points.get(team_key, 0)  # Updated field name

    # Save updated NC_Data.json
    with open(filename, "w") as file:
        json.dump(nc_data, file, indent=4)
    print(f"Updated {filename} with total ranking points.")

# Main Program
if __name__ == "__main__":
    update_nc_data("NC_Data.json")
