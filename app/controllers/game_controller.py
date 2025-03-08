# app/controllers/game_controller.py

from flask import Blueprint, jsonify, request
from app.models.game_manager import create_game, games 
from app.messaging import broadcast

game_bp = Blueprint('game', __name__, url_prefix='/game')

@game_bp.route('/start', methods=['GET'])
def start_game():
    new_game = create_game()
    new_game.start()  # Generate solution, etc.
    response = {
        "message": "New Clue-Less game started",
        "game_id": new_game.game_id
    }
    # Broadcast the new game state to all clients.
    broadcast("GameStarted", response)
    return jsonify(response)

@game_bp.route('/<int:game_id>/join', methods=['POST'])
def join_game(game_id):
    payload = request.get_json()
    player_name = payload.get("player_name") if payload else None
    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = game.add_player(player_name)
    response = {
        "message": f"Player {player.name} joined game {game_id}",
        "player_id": player.player_id,
        "game_id": game.game_id
    }
    # Broadcast updated game state.
    broadcast("PlayerJoined", response)
    return jsonify(response)

@game_bp.route('/<int:game_id>/move', methods=['POST'])
def move_player(game_id):
    payload = request.get_json()
    player_id = payload.get("player_id")
    new_room = payload.get("new_room")
    
    if not player_id or not new_room:
        return jsonify({"error": "Both player_id and new_room are required"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = game.move_player(player_id, new_room)
    if not player:
        return jsonify({"error": "Player not found in the game"}), 404

    response = {
        "message": f"Player {player.name} moved to {new_room}",
        "player_id": player.player_id,
        "current_room": player.current_room,
        "game_id": game.game_id
    }
    broadcast("PlayerMoved", response)
    return jsonify(response)

@game_bp.route('/<int:game_id>/rooms', methods=['GET'])
def get_rooms(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    room_names = [room.name for room in game.rooms]
    return jsonify({
        "rooms": room_names,
        "game_id": game.game_id
    })

@game_bp.route('/<int:game_id>/accuse', methods=['POST'])
def accuse(game_id):
    payload = request.get_json()
    player_id = payload.get("player_id")
    suspect = payload.get("suspect")
    weapon = payload.get("weapon")
    room = payload.get("room")
    
    if not player_id or not suspect or not weapon or not room:
        return jsonify({"error": "player_id, suspect, weapon, and room are required"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    correct = (
        game.solution["suspect"] == suspect and
        game.solution["weapon"] == weapon and
        game.solution["room"] == room
    )
    
    if correct:
        response = {
            "message": f"Accusation correct! Player {player_id} wins!",
            "solution": game.solution,
            "player_id": player_id,
            "game_id": game.game_id
        }
        broadcast("AccusationCorrect", response)
    else:
        response = {
            "message": f"Accusation incorrect. Player {player_id} is eliminated.",
            "player_id": player_id,
            "game_id": game.game_id
        }
        broadcast("AccusationIncorrect", response)
    
    return jsonify(response)



@game_bp.route('/<int:game_id>/turn', methods=['GET'])
def get_turn(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    current_player = game.get_current_player()
    if not current_player:
        return jsonify({"error": "No players in game"}), 400
    return jsonify({
        "game_id": game.game_id,
        "current_player": current_player.name,
        "player_id": current_player.player_id
    })

@game_bp.route('/<int:game_id>/turn/advance', methods=['POST'])
def advance_turn(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    new_player = game.advance_turn()
    if not new_player:
        return jsonify({"error": "No players in game"}), 400
    response = {
        "game_id": game.game_id,
        "current_player": new_player.name,
        "player_id": new_player.player_id
    }
    # Broadcast turn change.
    broadcast("TurnAdvanced", response)
    return jsonify(response)

@game_bp.route('/<int:game_id>/suggest', methods=['POST'])
def suggest(game_id):
    payload = request.get_json()
    player_id = payload.get("player_id")
    suspect = payload.get("suspect")
    weapon = payload.get("weapon")
    room = payload.get("room")
    
    if not player_id or not suspect or not weapon or not room:
         return jsonify({"error": "player_id, suspect, weapon, and room are required"}), 400
    
    game = games.get(game_id)
    if not game:
         return jsonify({"error": "Game not found"}), 404
    
    player = next((p for p in game.players if p.player_id == player_id), None)
    if not player:
         return jsonify({"error": "Player not found in the game"}), 404
         
    if player.current_room != room:
         return jsonify({"error": "Player must be in the suggested room to make a suggestion"}), 400
         
    response = {
         "message": f"Suggestion noted: {suspect} with the {weapon} in the {room}",
         "suggestion": {"suspect": suspect, "weapon": weapon, "room": room},
         "player_id": player_id,
         "game_id": game_id
    }
    broadcast("SuggestionMade", response)
    return jsonify(response)

@game_bp.route('/<int:game_id>/deal', methods=['POST'])
def deal(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    try:
        game.deal_cards()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    response = {
        "message": "Cards dealt to all players.",
        "game_id": game.game_id
    }
    # Broadcast card dealing event.
    broadcast("CardsDealt", response)
    return jsonify(response)

@game_bp.route('/<int:game_id>/player/<int:player_id>/hand', methods=['GET'])
def get_hand(game_id, player_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    player = next((p for p in game.players if p.player_id == player_id), None)
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({
        "player_id": player.player_id,
        "hand": player.hand,
        "game_id": game.game_id
    })


