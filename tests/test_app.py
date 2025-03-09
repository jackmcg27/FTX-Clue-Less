# tests/test_app.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from app.main import app

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello, World", response.data)

    def test_example_controller(self):
        response = self.app.get('/example/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('message'), 'Hello from the example controller')

    def test_game_start(self):
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("message"), "New Clue-Less game started")
        self.assertTrue("game_id" in data)

    def test_game_join(self):
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        join_payload = {"player_name": "Test Player"}
        response = self.app.post(f'/game/{game_id}/join', json=join_payload)
        self.assertEqual(response.status_code, 200)
        join_data = json.loads(response.data)
        self.assertEqual(join_data.get("game_id"), game_id)
        self.assertIsInstance(join_data.get("player_id"), int)
        self.assertGreater(join_data.get("player_id"), 0)

        self.assertIn("Test Player", join_data.get("message"))

    def test_game_move(self):
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        join_payload = {"player_name": "Mover"}
        response = self.app.post(f'/game/{game_id}/join', json=join_payload)
        self.assertEqual(response.status_code, 200)
        join_data = json.loads(response.data)
        player_id = join_data.get("player_id")
        move_payload = {"player_id": player_id, "new_room": "Kitchen"}
        response = self.app.post(f'/game/{game_id}/move', json=move_payload)
        self.assertEqual(response.status_code, 200)
        move_data = json.loads(response.data)
        self.assertEqual(move_data.get("current_room"), "Kitchen")
        self.assertEqual(move_data.get("player_id"), player_id)
        self.assertIn("Kitchen", move_data.get("message"))

    def test_get_rooms(self):
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        response = self.app.get(f'/game/{game_id}/rooms')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("rooms", data)
        self.assertEqual(data.get("game_id"), game_id)
        self.assertIn("Kitchen", data.get("rooms"))

    def test_game_accuse(self):
        # Start a new game
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        
        # Join a player
        join_payload = {"player_name": "Test Player"}
        response = self.app.post(f'/game/{game_id}/join', json=join_payload)
        self.assertEqual(response.status_code, 200)
        join_data = json.loads(response.data)
        player_id = join_data.get("player_id")
        
        # Retrieve the game instance from our in-memory store
        from app.models.game_manager import games
        game = games.get(game_id)
        self.assertIsNotNone(game.solution, "Game solution should be set when game starts")
        
        # Test wrong accusation with player_id included
        wrong_payload = {
            "player_id": player_id,
            "suspect": "Wrong Suspect",
            "weapon": "Wrong Weapon",
            "room": "Wrong Room"
        }
        response = self.app.post(f'/game/{game_id}/accuse', json=wrong_payload)
        self.assertEqual(response.status_code, 200)
        data_wrong = json.loads(response.data)
        self.assertIn("Accusation incorrect", data_wrong.get("message"))
        self.assertEqual(data_wrong.get("player_id"), player_id)
        
        # Test correct accusation using the game solution and including player_id
        correct_payload = {"player_id": player_id}
        correct_payload.update(game.solution)
        response = self.app.post(f'/game/{game_id}/accuse', json=correct_payload)
        self.assertEqual(response.status_code, 200)
        data_correct = json.loads(response.data)
        self.assertIn("Accusation correct", data_correct.get("message"))
        self.assertEqual(data_correct.get("solution"), game.solution)
        self.assertEqual(data_correct.get("player_id"), player_id)


    def test_turn_management(self):
        # Start a new game
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        # Join two players
        response = self.app.post(f'/game/{game_id}/join', json={"player_name": "Alice"})
        self.assertEqual(response.status_code, 200)
        response = self.app.post(f'/game/{game_id}/join', json={"player_name": "Bob"})
        self.assertEqual(response.status_code, 200)
        # Get current turn (should be Alice)
        response = self.app.get(f'/game/{game_id}/turn')
        self.assertEqual(response.status_code, 200)
        turn_data = json.loads(response.data)
        self.assertEqual(turn_data.get("current_player"), "Alice")
        # Advance turn (should now be Bob)
        response = self.app.post(f'/game/{game_id}/turn/advance')
        self.assertEqual(response.status_code, 200)
        turn_data = json.loads(response.data)
        self.assertEqual(turn_data.get("current_player"), "Bob")

    def test_game_suggestion(self):
        # Start a new game
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        
        # Join a player
        join_payload = {"player_name": "Suggester"}
        response = self.app.post(f'/game/{game_id}/join', json=join_payload)
        self.assertEqual(response.status_code, 200)
        join_data = json.loads(response.data)
        player_id = join_data.get("player_id")
        
        # Move the player to a room, e.g., "Library"
        move_payload = {"player_id": player_id, "new_room": "Library"}
        response = self.app.post(f'/game/{game_id}/move', json=move_payload)
        self.assertEqual(response.status_code, 200)
        
        # Make a suggestion from the same room ("Library")
        suggest_payload = {
            "player_id": player_id,
            "suspect": "Mrs. Peacock",
            "weapon": "Knife",
            "room": "Library"
        }
        response = self.app.post(f'/game/{game_id}/suggest', json=suggest_payload)
        self.assertEqual(response.status_code, 200)
        suggest_data = json.loads(response.data)
        self.assertIn("Suggestion noted", suggest_data.get("message"))

    def test_deal_cards(self):
        # Start a new game
        response = self.app.get('/game/start')
        self.assertEqual(response.status_code, 200)
        start_data = json.loads(response.data)
        game_id = start_data.get("game_id")
        
        # Join multiple players
        players = ["Alice", "Bob", "Charlie"]
        player_ids = []
        for name in players:
            join_payload = {"player_name": name}
            response = self.app.post(f'/game/{game_id}/join', json=join_payload)
            self.assertEqual(response.status_code, 200)
            join_data = json.loads(response.data)
            player_ids.append(join_data.get("player_id"))
        
        # Deal cards to all players
        response = self.app.post(f'/game/{game_id}/deal')
        self.assertEqual(response.status_code, 200)
        deal_data = json.loads(response.data)
        self.assertIn("Cards dealt", deal_data.get("message"))
        
        # Verify that each player's hand is not empty
        for pid in player_ids:
            response = self.app.get(f'/game/{game_id}/player/{pid}/hand')
            self.assertEqual(response.status_code, 200)
            hand_data = json.loads(response.data)
            self.assertTrue(len(hand_data.get("hand")) > 0)



if __name__ == '__main__':
    unittest.main()
