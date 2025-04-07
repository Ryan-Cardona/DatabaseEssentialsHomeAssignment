import requests  # Used to make HTTP requests to GitHub API
import json  # Used to save data as JSON
from datetime import datetime  # To add timestamps to each sprite entry

# GitHub API URL that lists the contents of the sprite folder
api_url = "https://api.github.com/repos/Purukitto/pokemon-data.json/contents/images/items/sprites"

# Base URL to access raw image files directly from GitHub
raw_base_url = "https://raw.githubusercontent.com/Purukitto/pokemon-data.json/master/images/items/sprites/"

# Make a GET request to the GitHub API to fetch the list of files
response = requests.get(api_url)

# Convert the JSON response to a Python list of file info
data = response.json()

# List to hold the sprite info for all .png files
sprites = []

# Loop through each file in the GitHub folder
for file in data:
    if file['name'].endswith(".png"):  # Only process PNG images
        sprite = {
            "filename": file['name'],  # The name of the sprite file
            "url": raw_base_url + file['name'],  # Full public URL to access the image
            "upload_time": datetime.utcnow().isoformat() + "Z"  # Add current timestamp in ISO format
        }
        sprites.append(sprite)  # Add this sprite to the list

# Save the sprite list as a JSON file
with open("sprites.json", "w") as f:
    json.dump(sprites, f, indent=2)  # Write nicely formatted JSON with indentation

print(f"✅ Generated {len(sprites)} sprites in sprites.json")