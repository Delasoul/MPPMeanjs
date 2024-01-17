import requests
import json
import time

# Replace with your own client ID and client secret
CLIENT_ID = "PATH-TO-YOUR-ID"
CLIENT_SECRET = ""

# Replace with the appropriate API endpoints for the simulator
API_BASE_URL = "https://simulator.home-connect.com"
AUTH_ENDPOINT = "/security/oauth/token"
APPLIANCES_ENDPOINT = "/api/homeappliances"
EVENTS_ENDPOINT = "/api/homeappliances/events"

# Global variable to store the latest state
latest_state = {}

# Authenticating and obtaining an access token
def authenticate():
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "IdentifyAppliance Monitor Control"
    }

    response = requests.post(API_BASE_URL + AUTH_ENDPOINT, data=auth_data)
    print("Authentication response status code:", response.status_code)
    print("Authentication response content:", response.text)

    if response.status_code == 200:
        access_token = json.loads(response.text)["access_token"]
        return access_token
    else:
        print("Authentication failed.")
        return None

# Retrieve the full state of all paired home appliances
def get_appliances_state(access_token):
    headers = {
        "Authorization": "Bearer " + access_token
    }

    appliances_url = API_BASE_URL + APPLIANCES_ENDPOINT
    response = requests.get(appliances_url, headers=headers)
    appliances_data = json.loads(response.text)
    return appliances_data

# Long polling for state changes
def long_poll_state_changes(access_token):
    headers = {
        "Authorization": "Bearer " + access_token
    }

    events_url = API_BASE_URL + EVENTS_ENDPOINT
    while True:
        response = requests.get(events_url, headers=headers, timeout=None, stream=True)
        if response.status_code == 200:
            for event in response.iter_lines():
                if event:
                    event_data = json.loads(event)
                    handle_event(event_data)
        else:
            print("Long polling request failed. Retrying...")
        time.sleep(1)  # Add a short delay between long polling requests

# Handle state change events
def handle_event(event_data):
    global latest_state

    if "items" in event_data and event_data["items"]:
        for item in event_data["items"]:
            appliance_id = item["homeAppliance"]["haid"]
            state = item["data"]["status"]
            latest_state[appliance_id] = state

            # Handle the state change according to your application's logic
            print("State change event for appliance", appliance_id)
            print(json.dumps(state, indent=4))
            print("-----------------------------------")

# Main program
def main():
    access_token = authenticate()

    if not access_token:
        print("Exiting program due to authentication failure.")
        return

    appliances_state = get_appliances_state(access_token)
    print("Appliances state:")
    print(json.dumps(appliances_state, indent=4))
    print("-----------------------------------")

    # ... The rest of your code for long polling and handling state changes ...

if __name__ == "__main__":
    main()
