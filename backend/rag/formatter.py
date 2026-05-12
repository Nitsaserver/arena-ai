def event_to_document(event: dict) -> str:
    return f"""
    Timestamp: {event.get('timestamp')}
    Round: {event.get('round')}
    Agent: {event.get('agent')}
    Team: {event.get('team')}
    Action: {event.get('action')}
    Target: {event.get('target')}
    Outcome: {event.get('outcome')}
    Details: {event.get('details', 'N/A')}
    """
