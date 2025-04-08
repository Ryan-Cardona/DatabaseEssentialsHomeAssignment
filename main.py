from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
import time

app = FastAPI()

# ✅ MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://ryan90121:ddVpx1gAfJN19AIp@cluster0.ojdbr8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client.multimedia_db

#Class for the player score
class PlayerScore(BaseModel):
    player_name: str
    score: int

# Checking if the MongoDB connection is successful
@app.on_event("startup")
async def init_db():
    print("Pinging MongoDB...")
    await db.command("ping")
    print("MongoDB connection successful")


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

    sprites = []  # This list will hold the documents fetched from the database

    try:
        # Use a try-except block to catch any MongoDB-related errors
        async for sprite in db.sprites.find():
            # Convert the MongoDB ObjectId to a string so it can be serialized in JSON
            sprite["_id"] = str(sprite["_id"])

            # Remove the binary 'content' field to prevent JSON serialization issues
            sprite.pop("content", None)

            # Add the cleaned-up document to our result list
            sprites.append(sprite)

        # Log how long the entire operation took
        print(f"✅ Completed /sprites in {time.time() - start:.2f} seconds")

    except Exception as e:
        # If an error occurs, print it to the logs and raise an HTTPException
        print(f"❌ Error fetching sprites: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sprites")

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
    start = time.time()  # Track how long the fetch takes
    print("✅ Starting /player_scores fetch...")

    scores = []  # List to store the documents from the collection

    try:
        # Loop through each document in the "scores" collection
        async for score in db.scores.find().limit(10):  # Use limit to prevent long fetches
            score["_id"] = str(score["_id"])  # Convert ObjectId to string for JSON
            scores.append(score)

        print(f"✅ Finished /player_scores in {time.time() - start:.2f} seconds")

    except Exception as e:
        # Print the error to Vercel logs for debugging
        print("❌ ERROR in /player_scores:", str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve player scores")

    # Return the list as a JSON response
    return scores

