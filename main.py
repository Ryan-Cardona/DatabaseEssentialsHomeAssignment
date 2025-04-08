from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
import time
import asyncio  # ⬅️ Needed for async sleep during retries

app = FastAPI()

# ✅ MongoDB connection
# The MongoDB client is created once and reused — important for serverless cold starts
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://ryan90121:ddVpx1gAfJN19AIp@cluster0.ojdbr8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client.multimedia_db

#Class for the player score
class PlayerScore(BaseModel):
    player_name: str
    score: int

# ⏳ Helper function that retries MongoDB queries up to MAX_RETRIES times
# Used by endpoints that fetch documents from collections
MAX_RETRIES = 3  # You can increase this if you expect more frequent failures

async def try_mongo_fetch(collection):
    for attempt in range(MAX_RETRIES):
        try:
            docs = []
            async for doc in collection.find().limit(10):  # ⏱️ Keep performance in mind
                doc["_id"] = str(doc["_id"])               # Convert ObjectId to string
                doc.pop("content", None)                   # Remove binary fields
                docs.append(doc)
            return docs
        except Exception as e:
            print(f"⚠️ MongoDB fetch failed (attempt {attempt + 1}): {e}")
            await asyncio.sleep(0.5)  # 🔁 Wait before retrying
    raise HTTPException(status_code=500, detail="Database unavailable after retries")

# Checking if the MongoDB connection is successful
@app.on_event("startup")
async def init_db():
    try:
        print("⏳ Pinging MongoDB on startup...")
        await db.command("ping")
        print("✅ MongoDB connection established.")
    except Exception as e:
        # 🧊 This can fail during cold start or concurrent triggers — safe to just log
        print("❌ MongoDB startup ping failed:", str(e))



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
    import time  # Used to measure how long the operation takes
    start = time.time()  # Store the start time for performance tracking
    print("✅ Starting /sprites fetch...")  # Log the start of the fetch process

    # Use retry-enabled fetch helper to avoid cold start failures
    sprites = await try_mongo_fetch(db.sprites)

    # Log how long the entire operation took
    print(f"✅ Completed /sprites in {time.time() - start:.2f} seconds")

    # Return the list of sprites as a JSON response
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
    start = time.time()
    print("✅ Starting /audio fetch...")

    # Use retry-enabled fetch helper
    audio_files = await try_mongo_fetch(db.audio)

    print(f"✅ Finished /audio in {time.time() - start:.2f} seconds")
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
    start = time.time()  # Track how long the fetch takes
    print("✅ Starting /player_scores fetch...")

    # Use retry-enabled fetch helper
    scores = await try_mongo_fetch(db.scores)

    print(f"✅ Finished /player_scores in {time.time() - start:.2f} seconds")
    return scores

# Define a root endpoint that returns a simple JSON message
@app.get("/")
async def root():
    return {"status": "running"}
