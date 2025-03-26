import requests
import json

# Replace with your Blue Alliance API key and district key
API_KEY = "8w7ZQ4zr57LL0SkFqrCRFU2yMPkKvYzCJAaNbNIAppB2lextbcjodNPnXWbLaStt"
DISTRICT_KEY = "2025fnc"  # Example: FIRST North Carolina District
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

def get_teams_in_district(district_key):
    """Fetch the list of teams in the given district."""
    url = f"https://www.thebluealliance.com/api/v3/district/{district_key}/teams"
    return fetch_data(url)

def get_all_matches(teams, year):
    """Fetch all matches for all teams in the district."""
    matches = {}
    base_url = "https://www.thebluealliance.com/api/v3/team/"
    for team in teams:
        team_key = team["key"]
        url = f"{base_url}{team_key}/matches/{year}"
        matches[team_key] = fetch_data(url)
    return matches

def get_real_rankings(district_key):
    """Fetch the district ranking points for teams."""
    url = f"https://www.thebluealliance.com/api/v3/district/{district_key}/rankings"
    return fetch_data(url)

def calculate_team_averages(matches):
    """Calculate the average alliance score for all teams."""
    averages = {}
    for team_key, match_data in matches.items():
        if not match_data:
            averages[team_key] = None
            continue
        total_score, match_count = 0, 0
        for match in match_data:
            alliances = match.get("alliances", {})
            red = alliances.get("red", {}).get("team_keys", [])
            blue = alliances.get("blue", {}).get("team_keys", [])
            score = alliances.get("red", {}).get("score", 0) if team_key in red else alliances.get("blue", {}).get("score", 0)
            if score > 0:
                total_score += score
                match_count += 1
        averages[team_key] = total_score / match_count if match_count > 0 else None
    return averages

def calculate_performance_index(teams, matches, averages):
    """Calculate the Performance Index (PI) for each team."""
    performance_index = {}
    for team in teams:
        team_key = team["key"]
        team_matches = matches.get(team_key, [])
        team_avg = averages.get(team_key, 0)
        total_pi, match_count = 0, 0

        for match in team_matches:
            alliances = match.get("alliances", {})
            red = alliances.get("red", {}).get("team_keys", [])
            blue = alliances.get("blue", {}).get("team_keys", [])
            partners = (
                [t for t in red if t != team_key] if team_key in red else
                [t for t in blue if t != team_key] if team_key in blue else
                []
            )

            if len(partners) == 2:
                partner1_avg = averages.get(partners[0], 0)
                partner2_avg = averages.get(partners[1], 0)
                total_pi += (team_avg * 3) - partner1_avg - partner2_avg
                match_count += 1

        performance_index[team_key] = total_pi / match_count if match_count > 0 else None
    return performance_index

def generate_json(teams, performance_index, rankings):
    """Generate a JSON file containing team data."""
    data = []
    for team in teams:
        team_key = team["key"]
        team_name = team.get("nickname", "Unknown Team")
        pi_value = performance_index.get(team_key, None)
        ranking_points = next((r["rank"] for r in rankings if r["team_key"] == team_key), None)

        data.append({
            "team_number": team_key,
            "team_name": team_name,
            "pi_value": pi_value,
            "ranking_points": ranking_points
        })

    # Sort by PI value (descending)
    data.sort(key=lambda x: x["pi_value"] if x["pi_value"] is not None else float('-inf'), reverse=True)

    # Add rank based on sorted order
    for i, item in enumerate(data, 1):
        item["pi_rank"] = i

    # Save to JSON file
    with open("NC_Data.json", "w") as file:
        json.dump(data, file, indent=4)

    print("Data successfully written to NC_Data.json.")

# Main Program
teams = get_teams_in_district(DISTRICT_KEY)
if teams:
    matches = get_all_matches(teams, YEAR)
    averages = calculate_team_averages(matches)
    performance_index = calculate_performance_index(teams, matches, averages)
    rankings = get_real_rankings(DISTRICT_KEY)
    generate_json(teams, performance_index, rankings)
else:
    print(f"No teams found for district {DISTRICT_KEY}.")
