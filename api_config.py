"""
API Configuration for FIFI Chatbot
Reads OpenAI API key from api_key.txt file
"""

import os

# Read API key from file
def load_api_key():
    key_file = os.path.join(os.path.dirname(__file__), "api_key.txt")
    with open(key_file, 'r') as f:
        return f.read().strip()

OPENAI_API_KEY = load_api_key()

# Optional: Model configuration
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4" if you have access
MAX_TOKENS = 1000
TEMPERATURE = 0.7
