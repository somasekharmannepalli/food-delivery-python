from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from config.database import get_database
from middleware.auth import require_auth
from bson import ObjectId

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.post("/add")
async def add_to_cart(request: Request):
    user_data = await require_auth(request)
    data = await request.json()
    item_id = data.get("itemId")
    
    if not item_id:
        return JSONResponse({"success": False, "message": "Item ID is required"})
    
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_data["user_id"])})
    cart_data = user.get("cartData", {})
    
    if item_id in cart_data:
        cart_data[item_id] += 1
    else:
        cart_data[item_id] = 1
        
    await db.users.update_one(
        {"_id": ObjectId(user_data["user_id"])},
        {"$set": {"cartData": cart_data}}
    )
    return JSONResponse({"success": True, "message": "Added to Cart"})

@router.post("/remove")
async def remove_from_cart(request: Request):
    user_data = await require_auth(request)
    data = await request.json()
    item_id = data.get("itemId")
    
    if not item_id:
        return JSONResponse({"success": False, "message": "Item ID is required"})
    
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_data["user_id"])})
    cart_data = user.get("cartData", {})
    
    if item_id in cart_data:
        if cart_data[item_id] > 1:
            cart_data[item_id] -= 1
        else:
            del cart_data[item_id]
            
    await db.users.update_one(
        {"_id": ObjectId(user_data["user_id"])},
        {"$set": {"cartData": cart_data}}
    )
    return JSONResponse({"success": True, "message": "Removed from Cart"})

@router.get("/get")
async def get_cart(request: Request):
    user_data = await require_auth(request)
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_data["user_id"])})
    return JSONResponse({"success": True, "cartData": user.get("cartData", {})})
