from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URL")

try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')  # Ping to test connection
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Could not connect to MongoDB:", str(e))