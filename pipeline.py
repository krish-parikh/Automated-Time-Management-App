from model import get_event_info
from input import parse_event_data
from priority import prioritisation

def pipeline(prompt, user_id):
    try:
        event_data = get_event_info(prompt)
        event_data = parse_event_data(event_data)
        for event in event_data:
            prioritisation(event=event, user_id=user_id)
            print('Event added to calendar')
        return
    except:
        return


prompt = 'I have an important exam this friday at 2pm need to revise for it on Tuesday morning.'

pipeline(prompt, 8)