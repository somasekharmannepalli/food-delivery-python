import asyncio
from config.database import connect_to_mongo, close_mongo_connection, get_database

async def seed():
    await connect_to_mongo()
    db = get_database()
    
    # Check if data already exists
    count = await db.foods.count_documents({})
    if count > 0:
        print("Data already seeded.")
        await close_mongo_connection()
        return
        
    food_items = [
        {
            "name": "Greek Salad",
            "image": "food/greek_salad.png",
            "price": 12,
            "description": "Food provides essential nutrients for overall health and well-being",
            "category": "Salad"
        },
        {
            "name": "Veg Salad",
            "image": "food/veg_salad.png",
            "price": 18,
            "description": "Food provides essential nutrients for overall health and well-being",
            "category": "Salad"
        },
        {
            "name": "Clover Salad",
            "image": "food/clover_salad.png",
            "price": 16,
            "description": "Food provides essential nutrients for overall health and well-being",
            "category": "Salad"
        },
        {
            "name": "Chicken Salad",
            "image": "food/chicken_salad.png",
            "price": 24,
            "description": "Food provides essential nutrients for overall health and well-being",
            "category": "Salad"
        },
        {
            "name": "Lasagna Rolls",
            "image": "food/lasagna_rolls.png",
            "price": 14,
            "description": "Food provides essential nutrients for overall health and well-being",
            "category": "Rolls"
        },
        {
            "name": "Peri Peri Rolls",
            "image": "food/peri_peri_rolls.png",
            "price": 12,
            "description": "Food provides essential nutrients for overall health and well-being",
            "category": "Rolls"
        }
    ]
    
    await db.foods.insert_many(food_items)
    print("✅ Seeded initial food items!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed())
