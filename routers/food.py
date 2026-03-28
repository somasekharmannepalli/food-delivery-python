import os
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from config.database import get_database
from middleware.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/food", tags=["food"])

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.get("/list")
async def list_foods(category: str = None):
    """List all food items, optionally filtered by category."""
    db = get_database()
    query = {}
    if category and category != "All":
        query["category"] = category

    foods = await db.foods.find(query).to_list(length=200)
    food_list = []
    for food in foods:
        food_list.append({
            "id": str(food["_id"]),
            "name": food["name"],
            "description": food["description"],
            "price": food["price"],
            "category": food["category"],
            "image": food.get("image", ""),
        })
    return JSONResponse({"success": True, "data": food_list})


@router.post("/add")
async def add_food(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
):
    """Add a new food item (admin only)."""
    user_data = await get_current_user(request)
    if not user_data or user_data.get("role") != "admin":
        return JSONResponse({"success": False, "message": "Admin access required"}, status_code=403)

    if not allowed_file(image.filename):
        return JSONResponse({"success": False, "message": "Invalid image format. Use PNG, JPG, GIF, or WebP."})

    Path("uploads/food").mkdir(parents=True, exist_ok=True)
    file_ext = image.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"uploads/food/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    db = get_database()
    food_doc = {
        "name": name,
        "description": description,
        "price": float(price),
        "category": category,
        "image": f"food/{filename}",
    }
    await db.foods.insert_one(food_doc)
    return JSONResponse({"success": True, "message": f"'{name}' added successfully!"})


@router.delete("/remove/{food_id}")
async def remove_food(food_id: str, request: Request):
    """Remove a food item (admin only)."""
    user_data = await get_current_user(request)
    if not user_data or user_data.get("role") != "admin":
        return JSONResponse({"success": False, "message": "Admin access required"}, status_code=403)

    db = get_database()
    food = await db.foods.find_one({"_id": ObjectId(food_id)})
    if food and food.get("image"):
        try:
            os.remove(f"uploads/{food['image']}")
        except FileNotFoundError:
            pass

    await db.foods.delete_one({"_id": ObjectId(food_id)})
    return JSONResponse({"success": True, "message": "Food item removed"})
