import requests

# Constants
BASE_URL = "http://0.0.0.0:8000"
LOGIN_ENDPOINT = "/login"
EVENTS_ENDPOINT = "/events"
CREATE_EVENT_ENDPOINT = "/create_event"

# User credentials
USER_EMAIL = "krish.parikh@me.com"
USER_PASSWORD = "1234"
    
def get_auth_token(email, password):
    response = requests.post(
        BASE_URL + LOGIN_ENDPOINT,
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None



def get_events(auth_token):
    """Get events for the authenticated user."""
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.get(BASE_URL + EVENTS_ENDPOINT, headers=headers)
    return response.json()

def register_user(username, password, email):
    """Register a new user."""
    response = requests.post(BASE_URL + "/register", json={"username": username, "password": password, "email": email})
    return response.json()

def create_event(auth_token, prompt):
    """Create an event for the authenticated user."""
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.post(BASE_URL + CREATE_EVENT_ENDPOINT, headers=headers, json={"prompt": prompt})
    return response.json()


if __name__ == "__main__":
    # Get an auth token for the user
    auth_token = get_auth_token(USER_EMAIL, USER_PASSWORD)
    # Create an event
    prompt = "I am meeting boss at work today aroung 6am and then goining out for a drink with my friend at 12pm."
    event = create_event(auth_token, prompt)
    print(event)


