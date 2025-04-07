from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio

import os  # Module to interact with the operating system (used for environment variables)
from dotenv import load_dotenv  # Loads environment variables from a .env file (optional but helpful for local dev)

app = FastAPI()

# Load environment variables from a .env file if it exists
load_dotenv()

# Retrieve the MongoDB connection string from an environment variable named 'MONGODB_URI'
MONGODB_URI = os.getenv("MONGODB_URI")

# Raise an error if the connection string is not set in the environment
if not MONGODB_URI:
    raise RuntimeError("❌ MONGODB_URI is not set in the environment variables.")

# Initialize the asynchronous MongoDB client with the URI
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

# Access the specific database you'll be using
db = client.multimedia_db

class PlayerScore(BaseModel):
    player_name: str
    score: int

@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

# Define a GET endpoint at the path "/sprites"
# When accessed, it will return all sprite documents from the "sprites" collection
@app.get("/sprites")
async def get_sprites():
    # Create an empty list to store the sprites we retrieve from MongoDB
    sprites = []

    # Use an asynchronous loop to fetch each document in the "sprites" collection
    async for sprite in db.sprites.find():
        # Convert the MongoDB ObjectId to a string so it can be returned in JSON format
        sprite["_id"] = str(sprite["_id"])

        # Remove the "content" field (binary data) to avoid serialization errors
        # JSON can't handle raw bytes, so we exclude it from the response
        sprite.pop("content", None)

        # Add the cleaned-up document to our list
        sprites.append(sprite)

    # Return the list of all sprite documents as a JSON response
    return sprites



@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

# Define a GET endpoint at the path "/audio"
# This endpoint will retrieve all audio documents from the "audio" collection
@app.get("/audio")
async def get_audio_files():
    # Create an empty list to store the audio documents
    audio_files = []

    # Use an asynchronous loop to go through each document in the "audio" collection
    async for audio in db.audio.find():
        # Convert the ObjectId to a string so it can be included in the JSON response
        audio["_id"] = str(audio["_id"])

        # Remove the binary "content" field from the document to prevent serialization errors
        audio.pop("content", None)

        # Add the cleaned document to our result list
        audio_files.append(audio)

    # Return the list of audio documents as a JSON response
    return audio_files


@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

# Define a GET endpoint at the path "/player_scores"
# This endpoint returns all player score documents from the "scores" collection
@app.get("/player_scores")
async def get_player_scores():
    # Create an empty list to store all retrieved player scores
    scores = []

    # Loop through each document in the "scores" collection using async MongoDB cursor
    async for score in db.scores.find():
        # Convert the ObjectId to a string so it's JSON-compatible
        score["_id"] = str(score["_id"])

        # Add the cleaned score document to the result list
        scores.append(score)

    # Return the list of scores as a JSON response
    return scores


# This defines a GET route for the root URL (http://127.0.0.1:8000)
# If a user accesses the root path, this function will be executed.
@app.get("/")
async def read_root():
    # Return a simple JSON response to confirm the API is running.
    return {"message": "Hello World"}


