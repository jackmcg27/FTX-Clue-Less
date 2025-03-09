# app/messaging.py

def broadcast(event, data):
    """
    Simulate a push-based notification to all connected clients.
    In the final system, this would send data via WebSockets or SSE.
    """
    print(f"[Real-Time Messaging] Event: {event} | Data: {data}")
