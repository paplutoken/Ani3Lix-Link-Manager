import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from models import Admin, Link
from auth import get_current_admin, create_access_token
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["itsdevilkun"]

app = FastAPI()

# CORS (Allows frontend to communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTES ----------------

# Admin Login
@app.post("/login")
async def login(admin: Admin):
    db_admin = db.admins.find_one({"username": admin.username, "password": admin.password})
    if db_admin:
        token = create_access_token({"username": admin.username})
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Get All Links (Public API)
@app.get("/links")
async def get_links():
    links = list(db.links.find({}, {"_id": 0}))
    return {"links": links}

# Add Link (Only Admins)
@app.post("/add_link")
async def add_link(link: Link, admin: dict = Depends(get_current_admin)):
    db.links.insert_one(link.dict())
    return {"message": "Link added successfully"}

# Delete Link (Only Admins)
@app.delete("/delete_link/{link_name}")
async def delete_link(link_name: str, admin: dict = Depends(get_current_admin)):
    db.links.delete_one({"name": link_name})
    return {"message": "Link deleted"}

# Get Active Admins
@app.get("/online_admins")
async def online_admins():
    admins = list(db.online_admins.find({}, {"_id": 0, "username": 1}))
    return {"active_admins": admins}

# Run Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
