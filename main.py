from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
import motor.motor_asyncio
import time

# Setup lifespan context to manage MongoDB connection lifecycle manually
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Initializing MongoDB client...")
    try:
        # Create and attach MongoDB client and DB to the app object
        app.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
            "mongodb+srv://ryan90121:ddVpx1gAfJN19AIp@cluster0.ojdbr8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
            serverSelectionTimeoutMS=3000  # Prevent long wait on errors
        )
        app.mongodb = app.mongodb_client.multimedia_db

        # Ping to ensure the connection is valid
        await app.mongodb.command("ping")
        print("✅ MongoDB connected.")
        yield
    finally:
        print("🔒 Closing MongoDB connection...")
        app.mongodb_client.close()

# Create FastAPI app with lifespan management
app = FastAPI(lifespan=lifespan)

# Define PlayerScore model
class PlayerScore(BaseModel):
    player_name: str
    score: int

@app.post("/upload_sprite")
async def upload_sprite(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await request.app.mongodb.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.get("/sprites")
async def get_sprites(request: Request):
    start = time.time()
    print("✅ Starting /sprites fetch...")
    try:
        # Convert MongoDB cursor to list (better than async for in serverless)
        sprites = await request.app.mongodb.sprites.find().to_list(length=10)
        for sprite in sprites:
            sprite["_id"] = str(sprite["_id"])
            sprite.pop("content", None)
        print(f"✅ Completed /sprites in {time.time() - start:.2f} seconds")
        return sprites
    except Exception as e:
        print(f"❌ Error in /sprites: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sprites")

@app.post("/upload_audio")
async def upload_audio(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await request.app.mongodb.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

@app.get("/audio")
async def get_audio_files(request: Request):
    start = time.time()
    print("✅ Starting /audio fetch...")
    try:
        audio_files = await request.app.mongodb.audio.find().to_list(length=10)
        for audio in audio_files:
            audio["_id"] = str(audio["_id"])
            audio.pop("content", None)
        print(f"✅ Finished /audio in {time.time() - start:.2f} seconds")
        return audio_files
    except Exception as e:
        print(f"❌ ERROR in /audio: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audio files")

@app.post("/player_score")
async def add_score(request: Request, score: PlayerScore):
    score_doc = score.dict()
    result = await request.app.mongodb.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

@app.get("/player_scores")
async def get_player_scores(request: Request):
    start = time.time()
    print("✅ Starting /player_scores fetch...")
    try:
        scores = await request.app.mongodb.scores.find().to_list(length=10)
        for score in scores:
            score["_id"] = str(score["_id"])
        print(f"✅ Finished /player_scores in {time.time() - start:.2f} seconds")
        return scores
    except Exception as e:
        print(f"❌ ERROR in /player_scores: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve player scores")

@app.get("/")
async def root():
    return {"status": "running"}
