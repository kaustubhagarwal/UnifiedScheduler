def deduplicate_events(events):
    """
    Removes duplicate events based on title and start time
    """
    seen = set()
    unique_events = []
    
    for event in events:
        event_key = (event['title'], event['start_time'])
        if event_key not in seen:
            seen.add(event_key)
            unique_events.append(event)
    
    return sorted(unique_events, key=lambda x: x['start_time'])
