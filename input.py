from datetime import datetime, timedelta, date
import re

def parse_time_string(time_str):
    time_str = time_str.lower().replace(" ", "")
    parts_of_day = ['morning', 'afternoon', 'evening', 'night', 'lunch', 'breakfast', 'dinner']

    if time_str in parts_of_day:
        if time_str == 'morning':
            return ['07:00', '09:00']
        elif time_str == 'afternoon':
            return ['15:00', '16:00']
        elif time_str == 'evening':
            return ['18:00', '20:00']
        elif time_str == 'night':
            return ['21:00', '00:00']
        elif time_str == 'lunch':
            return ['12:00', '13:00']
        elif time_str == 'breakfast':
            return ['06:00', '07:00']
        elif time_str == 'dinner':
            return ['18:00', '19:00']
    else:
        return ['12:00', '13:00']

def parse_date_string(date_str, current_date):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    phrases = ['tomorrow', 'today', 'yesterday', 'nextweek', 'nextmonth']

    date_str = date_str.lower().replace(" ", "")

    match_weekdays = re.search(r'\b(' + '|'.join(weekdays) + r')\b', date_str)
    match_phrase = re.search(r'\b(' + '|'.join(phrases) + r')\b', date_str)

    if match_weekdays:
        day_of_week = match_weekdays.group(0)
        days_difference = (weekdays.index(day_of_week) - current_date.weekday()) % 7
        return current_date + timedelta(days=days_difference)

    if match_phrase:
        date_str = match_phrase.group(0)
        if date_str == 'tomorrow':
            return current_date + timedelta(days=1)
        elif date_str == 'today':
            return current_date
        elif date_str == 'yesterday':
            return current_date - timedelta(days=1)
        elif date_str == 'nextweek':
            return current_date + timedelta(days=7)
        elif date_str == 'nextmonth':
            return current_date + timedelta(days=30)
    
    elif re.match(r'^\d{1,2},\d{1,2}$', date_str):
        day, month = map(int, date_str.split(','))
        return date(current_date.year, month, day)
    else:
        return current_date

def parse_time_range(time_str):
    if not time_str.strip():
        return ['14:00', '15:00']
    parts = time_str.replace(',', ' ').split()

    for part in parts:
        try:
            datetime.strptime(part, '%H:%M')
        except ValueError:
            return parse_time_string(part)
    
    if len(parts) == 1:
        return [parts[0], None]
    elif len(parts) >= 2:
        return [parts[0], parts[1]]
    else:
        return ['14:00', '15:00']

def adjust_time(time_str, add_hour):
    try:
        time = datetime.strptime(time_str, '%H:%M')
        adjusted_time = time + timedelta(hours=1) if add_hour else time - timedelta(hours=1)
    except ValueError:
        return None
    
    return adjusted_time.strftime('%H:%M')

def clean_event_info(response):
    current_date = datetime.now().date()

    for event in response['event_info']:
        if not event['event_name']:
            event['event_name'] = 'Unspecified'
        if not event['event_importance']:
            event['event_importance'] = '3'
        if not event['event_flexibility']:
            event['event_flexibility'] = '2'

        event_date_str = event.get('event_date', '')
        event['event_date'] = parse_date_string(event_date_str, current_date).strftime('%d, %m')

        start_time, end_time = parse_time_range(event.get('event_time', ''))
        if start_time and not end_time:
            end_time = adjust_time(start_time, True)
        elif not start_time and end_time:
            start_time = adjust_time(end_time, False)
        event['event_time'] = ', '.join(filter(None, [start_time, end_time]))

    return response

def parse_event_data(event_data):
    cleaned_data = clean_event_info(event_data)
    parsed_data = []
    current_date = datetime.now().date()
    current_year = current_date.year

    for event in cleaned_data['event_info']:
        day, month = map(int, event['event_date'].split(", "))
        event_year = current_year

        # Create a date object for the event
        event_date = date(event_year, month, day)
        # Check if the event date has already passed this year, adjust the year if necessary
        if event_date < current_date:
            event_year += 1
            event_date = date(event_year, month, day)

        start_datetime = end_datetime = None
        if event['event_time']:
            start_time, end_time = event['event_time'].split(", ")
            start_datetime = datetime.strptime(f"{event_date} {start_time}", '%Y-%m-%d %H:%M')
            end_datetime = datetime.strptime(f"{event_date} {end_time}", '%Y-%m-%d %H:%M')

        parsed_data.append({
            'event_name': event['event_name'],
            'event_date': event_date.strftime("%Y-%m-%d"),
            'start_datetime': start_datetime.strftime("%Y-%m-%d %H:%M:%S") if start_datetime else None,
            'end_datetime': end_datetime.strftime("%Y-%m-%d %H:%M:%S") if end_datetime else None,
            'event_importance': event['event_importance'],
            'event_flexibility': event['event_flexibility']
        })

    return parsed_data
