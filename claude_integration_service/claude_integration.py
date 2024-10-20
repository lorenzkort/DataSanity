import requests
import os

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

def send_to_claude(user_data):
    url = "https://api.claude.ai/your-endpoint"
    headers = {"Authorization": f"Bearer {CLAUDE_API_KEY}"}
    response = requests.post(url, json=user_data, headers=headers)
    return response.json()

# Simulate receiving a message from RabbitMQ (message queue integration)
# Assume user_data is a dictionary with user information
user_data = {"name": "John Doe"}
result = send_to_claude(user_data)
print(result)
