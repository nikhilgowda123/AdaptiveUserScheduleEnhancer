import datetime
from datetime import datetime as dddt
import icalendar
from icalendar import Event, vDatetime
import pytz

def convertdate(date):
    print(str(date))
    dt = dddt.fromisoformat(str(date).replace('Z', '+00:00'))
    output_string = dt.strftime('%Y-%m-%dT%H:%M')
    return output_string

def check_if_event_currentime(cal, now):
    for event in cal.walk():
        if isinstance(event, icalendar.Event):
            start_time = event.get('DTSTART').dt
            print(start_time)
            start_time = start_time.replace(tzinfo=pytz.UTC)
            end_time = event.get('DTEND').dt
            end_time = end_time.replace(tzinfo=pytz.UTC)
            if start_time <= now < end_time:
                # There is an event occurring at the current time
                print("There is an event occurring now:", event.get('SUMMARY'))
                endt = event.get('DTEND').dt
                print("Its ending at:", endt)
                return True, endt
    else:
        # There is no event occurring at the current time
        return False, "none"


def get_free_time_slots(start, end):
    with open('learn.ics', 'rb') as f:
        cal = icalendar.Calendar.from_ical(f.read())
    # Define the start and end times for the time range you want to search    
    start_time = dddt.strptime(start, '%Y-%m-%dT%H:%M')
    start_time = start_time.replace(tzinfo=pytz.UTC)
    print("dsfds", start_time)
    eventOn, endtime = check_if_event_currentime(cal, start_time)
    print(eventOn)
    if(eventOn):
        start_time = endtime
    end_time = dddt.strptime(end, '%Y-%m-%dT%H:%M')
    end_time = end_time.replace(tzinfo=pytz.UTC)
    # Parse the ICS file using the icalendar library
    # Extract the events within the time range
    events = [e for e in cal.walk() if isinstance(e, Event) and e.get('DTSTART').dt >= start_time and e.get('DTEND').dt <= end_time]

    # Calculate the un-allocated time periods
    gaps = []
    previous_end = start_time
    for event in events:
        current_start = event.get('DTSTART').dt
        gap = current_start - previous_end
        if gap > datetime.timedelta(0):
            gaps.append((convertdate(previous_end), convertdate(current_start)))
        previous_end = event.get('DTEND').dt

    # If the last event ends before the end of the time range, add a final gap
    if previous_end < end_time:
        gaps.append((convertdate(previous_end), convertdate(end_time)))

    # Print the un-allocated time periods
    for gap in gaps:
        print('Un-allocated time:', gap[0], '-', gap[1])

    return gaps



get_free_time_slots('2023-04-10T11:20', '2023-04-10T18:00')
