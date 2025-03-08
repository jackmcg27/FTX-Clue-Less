# app/models/game_manager.py

from app.models.game import Game

# In-memory storage for games
games = {}

def create_game():
    game = Game()
    games[game.game_id] = game
    return game
