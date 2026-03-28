import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_to_mongo():
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "tomato_food_delivery")
    db_instance.client = AsyncIOMotorClient(mongodb_url)
    db_instance.db = db_instance.client[db_name]
    print(f"✅ Connected to MongoDB database: '{db_name}'")


async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        print("🔌 Disconnected from MongoDB")


def get_database():
    return db_instance.db
