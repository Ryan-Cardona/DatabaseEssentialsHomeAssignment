from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
import motor.motor_asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file (used for local development)


# Setup lifespan context to manage MongoDB connection lifecycle manually
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\u23f3 Initializing MongoDB client...")
    try:
        # Load the MongoDB URI from environment variables for secure credential handling
        MONGODB_URI = os.getenv("MONGODB_URI")
        # Create MongoDB client and attach the database to the app object
        app.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        app.mongodb = app.mongodb_client.multimedia_db

        # Ping the database to verify connection
        await app.mongodb.command("ping")
        print("\u2705 MongoDB connected.")
        yield
    finally:
        # Close the MongoDB connection when the app shuts down
        print("\ud83d\udd12 Closing MongoDB connection...")
        app.mongodb_client.close()

# Create FastAPI app with lifespan management
app = FastAPI(lifespan=lifespan)

# Define PlayerScore model to validate incoming score data
class PlayerScore(BaseModel):
    player_name: str
    score: int

@app.post("/upload_sprite")
async def upload_sprite(request: Request, file: UploadFile = File(...)):
    # Read uploaded sprite file content and store it in MongoDB
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await request.app.mongodb.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.get("/sprites")
async def get_sprites(request: Request):
    start = time.time()
    print("\u2705 Starting /sprites fetch...")
    try:
        # Fetch up to 10 sprite documents from the database
        sprites = await request.app.mongodb.sprites.find()
        for sprite in sprites:
            # Convert ObjectId to string for JSON serialization
            sprite["_id"] = str(sprite["_id"])
            # Remove binary content to avoid issues during serialization
            sprite.pop("content", None)
        print(f"\u2705 Completed /sprites in {time.time() - start:.2f} seconds")
        return sprites
    except Exception as e:
        # Handle and report any errors that occur during the fetch
        print(f"❌ Error in /sprites: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sprites")

@app.post("/upload_audio")
async def upload_audio(request: Request, file: UploadFile = File(...)):
    # Read uploaded audio file content and store it in MongoDB
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await request.app.mongodb.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

@app.get("/audio")
async def get_audio_files(request: Request):
    start = time.time()
    print("\u2705 Starting /audio fetch...")
    try:
        # Fetch up to 10 audio file documents from the database
        audio_files = await request.app.mongodb.audio.find()
        for audio in audio_files:
            # Convert ObjectId to string for JSON serialization
            audio["_id"] = str(audio["_id"])
            # Remove binary content to avoid serialization issues
            audio.pop("content", None)
        print(f"\u2705 Finished /audio in {time.time() - start:.2f} seconds")
        return audio_files
    except Exception as e:
        # Handle and report any errors that occur during the fetch
        print(f"❌ ERROR in /audio: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audio files")

@app.post("/player_score")
async def add_score(request: Request, score: PlayerScore):
    # Insert new player score document into the scores collection
    score_doc = score.dict()
    result = await request.app.mongodb.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

@app.get("/player_scores")
async def get_player_scores(request: Request):
    start = time.time()
    print("\u2705 Starting /player_scores fetch...")
    try:
        # Fetch up to 10 player score documents from the database
        scores = await request.app.mongodb.scores.find()
        for score in scores:
            # Convert ObjectId to string for JSON serialization
            score["_id"] = str(score["_id"])
        print(f"\u2705 Finished /player_scores in {time.time() - start:.2f} seconds")
        return scores
    except Exception as e:
        # Handle and report any errors that occur during the fetch
        print(f"❌ ERROR in /player_scores: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve player scores")

@app.get("/")
async def root():
    # Simple root endpoint to confirm the server is running
    return {"status": "running"}
