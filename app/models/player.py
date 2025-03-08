# app/models/player.py

class Player:
    next_player_id = 1  # Class variable for auto-incrementing player IDs

    def __init__(self, name):
        self.player_id = Player.next_player_id
        Player.next_player_id += 1
        self.name = name
        self.current_room = None  # Track player's current room
        self.hand = []          # New attribute to hold dealt cards
