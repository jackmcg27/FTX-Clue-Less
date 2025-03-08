# app/controllers/example_controller.py

from flask import Blueprint, jsonify

# Create a Blueprint named 'example' with URL prefix '/example'
example_bp = Blueprint('example', __name__, url_prefix='/example')

@example_bp.route('/')
def example_home():
    return jsonify({'message': 'Hello from the example controller'})
