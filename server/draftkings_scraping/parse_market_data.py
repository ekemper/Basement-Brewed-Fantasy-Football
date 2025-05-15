import json
import os
import sys
from pprint import pprint

def find_event_markets(json_path, event_id):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Try to find the event by ID
    events = data.get('events', [])
    event = None
    for e in events:
        if str(e.get('id')) == str(event_id):
            event = e
            break
    if not event:
        print(f"Event ID {event_id} not found in {json_path}")
        return

    print(f"Found event: {event.get('name')}")
    print("\nEvent data keys:", list(event.keys()))

    # Print all keys/sections that might contain market/odds data
    for key in event:
        if any(x in key.lower() for x in ['market', 'prop', 'odds', 'yard', 'player']):
            print(f"\nSection: {key}")
            pprint(event[key])

    # Print the whole event if nothing obvious is found
    print("\nFull event data (truncated):")
    pprint({k: event[k] for k in list(event.keys())[:5]})

if __name__ == "__main__":
    # Default file and event ID
    json_path = os.path.join(os.path.dirname(__file__), 'network_responses', 'response_106.json')
    event_id = 32225662
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    if len(sys.argv) > 2:
        event_id = sys.argv[2]
    find_event_markets(json_path, event_id) 