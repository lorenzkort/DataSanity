from flask import Flask
import os

app = Flask(__name__)

# Load API key from environment variable
app.config["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY")

# Debug: Print API key presence
print(
    f"API Key present in app config: {'Yes' if app.config['ANTHROPIC_API_KEY'] else 'No'}"
)

from app import routes
