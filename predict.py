import requests
import json

# Replace with your Blue Alliance API key
API_KEY = "8w7ZQ4zr57LL0SkFqrCRFU2yMPkKvYzCJAaNbNIAppB2lextbcjodNPnXWbLaStt"
YEAR = 2025  # Replace with the desired year

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

def get_event_matches(event_key):
    """Fetch all matches for a given event."""
    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches"
    return fetch_data(url)

def calculate_predicted_winner(match, pi_scores):
    """Calculate the predicted winner based on PI scores."""
    alliances = match.get("alliances", {})
    red_alliance = alliances.get("red", {}).get("team_keys", [])
    blue_alliance = alliances.get("blue", {}).get("team_keys", [])

    red_score = sum(pi_scores.get(team, 0) for team in red_alliance)
    blue_score = sum(pi_scores.get(team, 0) for team in blue_alliance)

    predicted_winner = "red" if red_score > blue_score else "blue"
    return predicted_winner

def load_pi_scores(filename="NC_Data.json"):
    """Load PI scores from the NC_Data.json file."""
    try:
        with open(filename, "r") as file:
            teams = json.load(file)
            return {team["team_number"]: team["pi_value"] for team in teams}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading PI scores from {filename}: {e}")
        return {}

def generate_event_data(events, pi_scores):
    """Generate match data for each event and save it as JSON."""
    for event in events:
        event_key = event["key"]
        event_name = event["name"]
        matches = get_event_matches(event_key)

        if not matches:
            print(f"No matches found for event {event_name}.")
            continue

        match_data = []
        for match in matches:
            match_number = match.get("match_number")
            real_winner = match.get("winning_alliance", "N/A")
            predicted_winner = calculate_predicted_winner(match, pi_scores)

            # Include the teams for both alliances
            alliances = match.get("alliances", {})
            red_teams = alliances.get("red", {}).get("team_keys", [])
            blue_teams = alliances.get("blue", {}).get("team_keys", [])

            match_data.append({
                "match_number": match_number,
                "predicted_winner": predicted_winner,
                "real_winner": real_winner,
                "red_teams": red_teams,
                "blue_teams": blue_teams
            })

        # Save match data as JSON
        filename = f"{event_key}.json"
        with open(filename, "w") as file:
            json.dump(match_data, file, indent=4)
        print(f"Data for {event_name} saved to {filename}")

# Main Program
pi_scores = load_pi_scores("NC_Data.json")  # Load PI scores from the JSON file
if not pi_scores:
    print("No PI scores loaded. Ensure NC_Data.json is present and correctly formatted.")

events = get_nc_events()
if events:
    generate_event_data(events, pi_scores)
else:
    print("No events found for North Carolina district.")
