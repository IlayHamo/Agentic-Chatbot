import requests
from dotenv import load_dotenv
import os

# Load .env from the same directory as this script
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path)

student_id = os.getenv("ID")
password = os.getenv("password")

url = "https://server.iac.ac.il/api/v1/studentapi/generate_key"
payload = {"id": student_id, "password": password}

response = requests.post(url, json=payload).json()
print(response)

api_key = response.get("api_key") or response.get("key") or response.get("token")
if api_key:
    print(f"\nAPI Key: {api_key}")
    # Save the API key back to the .env file
    with open(dotenv_path, "r") as f:
        env_content = f.read()
    env_content = env_content.replace('API_KEY = ""', f'API_KEY = "{api_key}"')
    with open(dotenv_path, "w") as f:
        f.write(env_content)
    print("API key saved to .env")
