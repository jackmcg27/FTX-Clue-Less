# app/messaging.py

# Dictionary mapping client IDs to lists of messages
subscribers = {}

def subscribe(client_id):
    """Register a client for receiving broadcast messages."""
    if client_id not in subscribers:
        subscribers[client_id] = []
    return subscribers[client_id]

def get_messages(client_id):
    """Return the list of messages for a client."""
    return subscribers.get(client_id, [])

def clear_messages(client_id):
    """Clear the message queue for a client."""
    if client_id in subscribers:
        subscribers[client_id] = []

def broadcast(event, data):
    """
    Simulate a push-based notification by appending the message
    to every subscriber's queue.
    """
    message = f"Event: {event} | Data: {data}"
    print(f"[Real-Time Messaging] {message}")
    # Append the message to each subscriber's queue.
    for client in subscribers.keys():
        subscribers[client].append(message)
