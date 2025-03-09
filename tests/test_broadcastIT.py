import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
import json
from app.main import app

class BroadcastIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_player_join_broadcast(self):
        # Patch the broadcast function in the game_controller module.
        with patch('app.controllers.game_controller.broadcast') as mock_broadcast:
            # Start a new game
            response = self.client.get('/game/start')
            self.assertEqual(response.status_code, 200)
            start_data = json.loads(response.data)
            game_id = start_data.get("game_id")
            
            # Join a player
            join_payload = {"player_name": "Alice"}
            response = self.client.post(f'/game/{game_id}/join', json=join_payload)
            self.assertEqual(response.status_code, 200)
            
            # Verify that broadcast was called with "PlayerJoined" event.
            mock_broadcast.assert_called_with("PlayerJoined", unittest.mock.ANY)

if __name__ == '__main__':
    unittest.main()
