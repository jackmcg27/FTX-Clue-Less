# app/messaging.py

from app.socketio_instance import socketio

def broadcast(event, data):
    """
    Use SocketIO to emit the event to all connected clients.
    """
    socketio.emit(event, data)
    print(f"[SocketIO Broadcast] Event: {event} | Data: {data}")
