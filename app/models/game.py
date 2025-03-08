# app/models/game.py

import random
from app.models.player import Player
from app.models.room import Room

class Game:
    next_game_id = 1  # Class variable to auto-increment game IDs

    def __init__(self):
        self.game_id = Game.next_game_id
        Game.next_game_id += 1
        self.players = []  # Holds Player instances
        self.started = False
        # Initialize default rooms
        self.rooms = [Room(name) for name in [
            "Kitchen", "Ballroom", "Conservatory", "Dining Room",
            "Billiard Room", "Library", "Lounge", "Hall", "Study"
        ]]
        # Define lists for suspects and weapons (used in accusation)
        self.suspects = [
            "Miss Scarlet", "Colonel Mustard", "Mrs. White",
            "Mr. Green", "Mrs. Peacock", "Professor Plum"
        ]
        self.weapons = [
            "Candlestick", "Knife", "Lead Pipe",
            "Revolver", "Rope", "Wrench"
        ]
        self.solution = None  # Will be set when the game starts
        self.current_turn_index = 0  # Tracks which player's turn it is

    def start(self):
        self.started = True
        # Randomly choose one suspect, one weapon, and one room as the solution
        self.solution = {
            "suspect": random.choice(self.suspects),
            "weapon": random.choice(self.weapons),
            "room": random.choice([room.name for room in self.rooms])
        }

    def add_player(self, player_name):
        """Create a new Player and add them to the game."""
        player = Player(player_name)
        self.players.append(player)
        # If this is the first player, set the turn to them
        if len(self.players) == 1:
            self.current_turn_index = 0
        return player

    def move_player(self, player_id, new_room):
        """Move the specified player to a new room."""
        for player in self.players:
            if player.player_id == player_id:
                player.current_room = new_room
                return player
        return None

    def get_current_player(self):
        """Return the player whose turn it is."""
        if self.players:
            return self.players[self.current_turn_index]
        return None

    def advance_turn(self):
        """Advance the turn to the next player (round-robin)."""
        if self.players:
            self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
            return self.get_current_player()
        return None

    def deal_cards(self):
        if self.solution is None:
            raise Exception("Game hasn't started or solution not set")
        deck = []
        # Build the deck excluding the solution cards
        deck.extend([s for s in self.suspects if s != self.solution["suspect"]])
        deck.extend([w for w in self.weapons if w != self.solution["weapon"]])
        deck.extend([room.name for room in self.rooms if room.name != self.solution["room"]])
        import random
        random.shuffle(deck)
        num_players = len(self.players)
        if num_players == 0:
            return
        # Distribute cards round-robin
        for i, card in enumerate(deck):
            self.players[i % num_players].hand.append(card)
