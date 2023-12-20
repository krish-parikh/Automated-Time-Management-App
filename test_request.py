import requests

# Constants
BASE_URL = "http://44.204.24.198"
LOGIN_ENDPOINT = "/login"
EVENTS_ENDPOINT = "/events"
CREATE_EVENT_ENDPOINT = "/create_event"
API_KEY = "BDeZnpabL9xww0i7//92MTheqnOzKZg4LK+Zu6w8ERk="  # Your API key

# User credentials
USER_EMAIL = "krish.parikh@me.com"
USER_PASSWORD = "1234"

def get_auth_token(email, password):
    headers = {"X-Api-Key": API_KEY}
    response = requests.post(
        BASE_URL + LOGIN_ENDPOINT,
        headers=headers,
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_events(auth_token):
    """Get events for the authenticated user."""
    headers = {
        'Authorization': f'Bearer {auth_token}',
        "X-Api-Key": API_KEY
    }
    response = requests.get(BASE_URL + EVENTS_ENDPOINT, headers=headers)
    return response.json()

def register_user(username, password, email):
    """Register a new user."""
    headers = {"X-Api-Key": API_KEY}
    response = requests.post(
        BASE_URL + "/register", 
        headers=headers, 
        json={"username": username, "password": password, "email": email}
    )
    return response.json()

def create_event(auth_token, prompt):
    """Create an event for the authenticated user."""
    headers = {
        'Authorization': f'Bearer {auth_token}',
        "X-Api-Key": API_KEY
    }
    response = requests.post(
        BASE_URL + CREATE_EVENT_ENDPOINT, 
        headers=headers, 
        json={"prompt": prompt}
    )
    return response.json()

if __name__ == "__main__":
    # Get an auth token for the user
    auth_token = get_auth_token(USER_EMAIL, USER_PASSWORD)
    if auth_token:
        print(get_events(auth_token))

