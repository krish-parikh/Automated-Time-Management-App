import sqlite3
from datetime import datetime, timedelta

def check_date(user_id, event_date):
    # Connect to the SQLite database
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()

    # Get the events
    query = 'SELECT * FROM events WHERE user_id = ? AND date(event_date) = ?'
    cursor.execute(query, (user_id, event_date))
    events = cursor.fetchall()

    # Create a dictionary with events
    event_dict = {}
    for event in events:
        event_id, user_id, event_name, start_datetime, end_datetime, event_date, event_flexibility, event_importance = event
        event_dict[event_id] = {
            'user_id': user_id,
            'event_name': event_name,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'event_date': event_date,
            'event_flexibility': event_flexibility,
            'event_importance': event_importance
        }

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return event_dict

def check_event_time_gap(event_id):
    """
    Check the start and end time gap of an event.
    """

    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT start_datetime, end_datetime FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    if event and event[0] and event[1]:
        start_time = datetime.strptime(event[0], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S")
        return (end_time - start_time).total_seconds() / 3600  # Return gap in hours
    return 0

def check_movability(event_id):
    """
    Check the movability of an event.
    """
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT event_flexibility FROM events WHERE id = ?", (event_id,))
    movability = cursor.fetchone()
    return movability[0] if movability else None

def check_priority(event_id):
    """
    Check the priority of an event.
    """
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT event_importance FROM events WHERE id = ?", (event_id,))
    priority = cursor.fetchone()
    return priority[0] if priority else None

def is_conflict(event1, event2):
    """
    Check if two events conflict.
    """
    start1, end1 = event1['start_datetime'], event1['end_datetime']
    start2, end2 = event2['start_datetime'], event2['end_datetime']
    return max(start1, start2) < min(end1, end2)

def find_conflicting_event(user_id, event, event_date):
    conflicting_event_id = None
    for event_id, other_event in check_date(user_id=user_id, event_date=event_date).items():
        if is_conflict(event, other_event):
            conflicting_event_id = event_id
            break
    return conflicting_event_id

def add_event(user_id, event):
    """
    Add an event to the events table.
    """
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (user_id, event_name, start_datetime, end_datetime, event_date, event_flexibility, event_importance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, event['event_name'], event['start_datetime'], event['end_datetime'], event['event_date'], event['event_flexibility'], event['event_importance']))
    
    event_id = cursor.lastrowid  # Get the ID of the newly inserted row
    
    conn.commit()
    conn.close()
    
    return event_id  # Return the event ID


def is_time_slot_available(event_id, start_time, end_time, user_id):
    """
    Check if a given time slot is available.
    """
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_flexibility FROM events WHERE user_id = ? AND ((start_datetime < ? AND end_datetime > ?) AND id != ?)", (user_id, end_time, start_time, event_id))
    overlapping_events = cursor.fetchall()

    current_event_movability = check_movability(event_id)

    for overlap_event in overlapping_events:
        overlap_id, overlap_flexibility = overlap_event
        if current_event_movability == 1 and overlap_flexibility == 2:
            # If the current event is more flexible, reorganise the overlapping event
            gap_hours = check_event_time_gap(overlap_id)
            reorganise_event(overlap_id, gap_hours, user_id)
        else:
            # If the current event is less flexible or equally flexible, the slot is not available
            return False

    return True

def find_new_time_slot(event_id, gap_hours, user_id):
    """
    Find the nearest available new time slot for the event.
    """
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()

    # Fetch the event details
    cursor.execute("SELECT start_datetime, end_datetime FROM events WHERE user_id = ? AND id = ?", (user_id, event_id,))
    event = cursor.fetchone()
    if not event:
        return None

    original_start = datetime.strptime(event[0], "%Y-%m-%d %H:%M:%S")
    original_end = datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S")
    gap = timedelta(hours=gap_hours)

    # Collect all event times on the same day for the specific user to avoid these slots
    event_date = original_start.date()
    cursor.execute("SELECT start_datetime, end_datetime FROM events WHERE user_id = ? AND date(start_datetime) = ? AND id != ?", (user_id, event_date, event_id))
    existing_events = cursor.fetchall()
    occupied_slots = [(datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S"), datetime.strptime(e[1], "%Y-%m-%d %H:%M:%S")) for e in existing_events]

    # Function to check if a time slot overlaps with existing events
    def is_slot_occupied(start, end):
        for s, e in occupied_slots:
            if max(start, s) < min(end, e):
                return True
        return False

    # Check for slots before and after the original start time
    potential_start_times = []
    new_start_time = original_start - gap
    while new_start_time >= datetime(original_start.year, original_start.month, original_start.day, 0, 0, 0):
        if not is_slot_occupied(new_start_time, new_start_time + gap):
            potential_start_times.append(new_start_time)
        new_start_time -= gap

    new_start_time = original_end
    while new_start_time + gap <= datetime(original_end.year, original_end.month, original_end.day, 23, 59, 59):
        if not is_slot_occupied(new_start_time, new_start_time + gap):
            potential_start_times.append(new_start_time)
        new_start_time += gap

    # Sort potential start times by proximity to the original start time and check availability
    potential_start_times.sort(key=lambda x: abs((x - original_start).total_seconds()))
    for new_start_time in potential_start_times:
        new_end_time = new_start_time + gap
        if is_time_slot_available(event_id, new_start_time, new_end_time, user_id):
            return new_start_time

    return None


def reorganise_event(event_id, gap_hours, user_id):
    """
    Reorganise an event to a new time slot.
    """
    new_start_time = find_new_time_slot(event_id, gap_hours, user_id)
    if new_start_time:
        conn = sqlite3.connect('calendar_app.db')
        cursor = conn.cursor()
        new_end_time = new_start_time + timedelta(hours=gap_hours)
        cursor.execute("UPDATE events SET start_datetime = ?, end_datetime = ? WHERE user_id = ? AND id = ?", 
                       (new_start_time.strftime("%Y-%m-%d %H:%M:%S"), new_end_time.strftime("%Y-%m-%d %H:%M:%S"), user_id, event_id))
        conn.commit()
        conn.close()
        print("Event ID:", event_id, "reorganised to", new_start_time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("No suitable time slot found for event ID:", event_id)

event = {'event_name': "Test6", 'event_date': '2023-12-05', 'start_datetime': '2023-12-05 12:00:00', 'end_datetime': '2023-12-05 12:10:00', 'event_importance': '5', 'event_flexibility': '2'}

def prioritisation(event, user_id):
    """
    Check the priority of an event and reorganise if necessary.
    """
    # First, check if the event is conflicting
    conflicting_event_id = find_conflicting_event(user_id=user_id, event=event, event_date=event['event_date'])
    
    if conflicting_event_id is None:
        # Add the event if there is no conflict
        event_id = add_event(event=event, user_id=user_id)
        return "Event added successfully, no conflicts."

    else:
        # Add the event since we know there's a conflict
        event_id = add_event(event=event, user_id=user_id)

        # Retrieve priority and flexibility for both events
        input_event_priority = check_priority(event_id)
        input_event_flexibility = check_movability(event_id)
        conflicting_event_priority = check_priority(conflicting_event_id)
        conflicting_event_flexibility = check_movability(conflicting_event_id)

        # Handle conflicts based on flexibility and priority
        if input_event_flexibility == 1 and conflicting_event_flexibility == 2:
            reorganise_event(conflicting_event_id, check_event_time_gap(conflicting_event_id), user_id)
            return "Conflicting event reorganised due to higher flexibility of the new event."

        elif input_event_flexibility == 2 and conflicting_event_flexibility == 1:
            reorganise_event(event_id, check_event_time_gap(event_id), user_id)
            return "New event reorganised due to lower flexibility."

        elif input_event_flexibility == conflicting_event_flexibility:
            if input_event_priority > conflicting_event_priority:
                reorganise_event(conflicting_event_id, check_event_time_gap(conflicting_event_id), user_id)
                return "Conflicting event reorganised due to higher priority of the new event."

            elif input_event_priority == conflicting_event_priority:
                if input_event_flexibility == 1:
                    reorganise_event(conflicting_event_id, check_event_time_gap(conflicting_event_id), user_id)
                    return "Conflicting event reorganised, equal priority and flexibility."
                else:
                    reorganise_event(event_id, check_event_time_gap(event_id), user_id)
                    return "New event reorganised, equal priority and flexibility."

            else:
                reorganise_event(event_id, check_event_time_gap(event_id), user_id)
                return "New event reorganised due to lower priority."
        else:
            return "Event conflict exists, but no reorganisation due to equal flexibility."


event = [{'event_name': 'Birthday', 'event_date': '2023-12-08', 'start_datetime': '2023-12-08 09:00:00', 'end_datetime': '2023-12-08 10:00:00', 'event_importance': '5', 'event_flexibility': '1'}, {'event_name': "Sleep", 'event_date': '2023-12-15', 'start_datetime': '2023-12-15 18:00:00', 'end_datetime': '2023-12-15 19:00:00', 'event_importance': '4', 'event_flexibility': '2'}]

