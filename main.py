from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import os
import time

app = FastAPI()

# Allow CORS for testing/debugging (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client connection setup
mongo_uri = os.getenv("MONGO_URI") or "mongodb+srv://ryan90121:ddVpx1gAfJN19AIp@cluster0.ojdbr8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
db = client.multimedia_db

# On FastAPI startup, ping the MongoDB server to confirm the connection
@app.on_event("startup")
async def init_db():
    try:
        print("⏳ Pinging MongoDB on startup...")
        await db.command("ping")
        print("✅ MongoDB connection established.")
    except Exception as e:
        print("❌ MongoDB startup ping failed:", str(e))

# Define a GET endpoint at the root path to check if the server is alive
@app.get("/")
async def root():
    return {"status": "running"}

# Define a GET endpoint at the path "/sprites"
# This endpoint returns all sprite documents from the "sprites" collection
@app.get("/sprites")
async def get_sprites():
    start = time.time()
    print("✅ Starting /sprites fetch...")

    sprites = []  # Create an empty list to store all retrieved sprites

    try:
        # Loop through each document in the "sprites" collection using async MongoDB cursor
        async for sprite in db.sprites.find().limit(10):
            # Convert the ObjectId to a string so it's JSON-compatible
            sprite["_id"] = str(sprite["_id"])

            # Remove the binary 'content' field to avoid serialization issues
            sprite.pop("content", None)

            # Add the cleaned sprite document to the result list
            sprites.append(sprite)

        print(f"✅ Completed /sprites in {time.time() - start:.2f} seconds")

    except Exception as e:
        # If anything goes wrong, print the full error to the log and raise a 500 error
        print("❌ ERROR in /sprites:", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch sprites")

    # Return the list of sprites as a JSON response
    return sprites

# Define a GET endpoint at the path "/audio"
# This endpoint returns all audio file documents from the "audio" collection
@app.get("/audio")
async def get_audio_files():
    start = time.time()
    print("✅ Starting /audio fetch...")

    audio_files = []  # Create an empty list to store all retrieved audio files

    try:
        # Loop through each document in the "audio" collection using async MongoDB cursor
        async for audio in db.audio.find().limit(10):
            # Convert the ObjectId to a string so it's JSON-compatible
            audio["_id"] = str(audio["_id"])

            # Remove the binary 'content' field to avoid serialization issues
            audio.pop("content", None)

            # Add the cleaned audio document to the result list
            audio_files.append(audio)

        print(f"✅ Completed /audio in {time.time() - start:.2f} seconds")

    except Exception as e:
        # If anything goes wrong, print the full error to the log and raise a 500 error
        print("❌ ERROR in /audio:", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch audio files")

    # Return the list of audio files as a JSON response
    return audio_files

# Define a GET endpoint at the path "/player_scores"
# This endpoint returns all player score documents from the "scores" collection
@app.get("/player_scores")
async def get_player_scores():
    start = time.time()
    print("✅ Starting /player_scores fetch...")

    scores = []  # Create an empty list to store all retrieved player scores

    try:
        # Loop through each document in the "scores" collection using async MongoDB cursor
        async for score in db.scores.find().limit(10):
            # Convert the ObjectId to a string so it's JSON-compatible
            score["_id"] = str(score["_id"])

            # Add the cleaned score document to the result list
            scores.append(score)

        print(f"✅ Completed /player_scores in {time.time() - start:.2f} seconds")

    except Exception as e:
        # If anything goes wrong, print the full error to the log and raise a 500 error
        print("❌ ERROR in /player_scores:", str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve player scores")

    # Return the list of scores as a JSON response
    return scores