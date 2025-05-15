import json
import os
from pprint import pprint

def find_event_markets_in_file(json_path, event_id):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Could not load {json_path}: {e}")
        return False

    found = False
    # Try to find the event by ID in various possible structures
    if isinstance(data, dict):
        # 1. events list
        events = data.get('events', [])
        if isinstance(events, list):
            for e in events:
                if str(e.get('id')) == str(event_id):
                    print(f"\n=== {json_path} ===")
                    print(f"Found event: {e.get('name')}")
                    for key in e:
                        if any(x in key.lower() for x in ['market', 'prop', 'odds', 'yard', 'player']):
                            print(f"Section: {key}")
                            pprint(e[key])
                            found = True
        # 2. Flat dict with event id as key
        if str(event_id) in data:
            print(f"\n=== {json_path} ===")
            print(f"Found event by key: {event_id}")
            pprint(data[str(event_id)])
            found = True
        # 3. Top-level keys with market/odds/props
        for key in data:
            if any(x in key.lower() for x in ['market', 'prop', 'odds', 'yard', 'player']):
                print(f"\n=== {json_path} ===")
                print(f"Section: {key}")
                pprint(data[key])
                found = True
    return found

def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'network_responses')
    event_id = 32225662
    files = [f for f in os.listdir(base_dir) if f.endswith('.json')]
    any_found = False
    for fname in files:
        fpath = os.path.join(base_dir, fname)
        if find_event_markets_in_file(fpath, event_id):
            any_found = True
    if not any_found:
        print("No relevant market/odds/props data found for the event in any JSON file.")

if __name__ == "__main__":
    main() 