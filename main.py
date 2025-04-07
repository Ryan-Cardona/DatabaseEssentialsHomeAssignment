from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio

app = FastAPI()

# ✅ MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://ryan90121:ddVpx1gAfJN19AIp@cluster0.ojdbr8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
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



@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}
