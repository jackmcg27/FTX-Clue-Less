# app/main.py

from flask import Flask
from app.controllers.example_controller import example_bp
from app.controllers.game_controller import game_bp

app = Flask(__name__)
app.config.from_pyfile('config.py')  # Loads configuration from config.py

# Register blueprints
app.register_blueprint(example_bp)
app.register_blueprint(game_bp)

@app.route('/')
def home():
    return "Hello, World! This is your Clue-Less game!"

if __name__ == '__main__':
    app.run(debug=True)
