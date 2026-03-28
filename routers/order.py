import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from config.database import get_database
from middleware.auth import require_auth
from bson import ObjectId

router = APIRouter(prefix="/api/order", tags=["order"])

@router.post("/place")
async def place_order(request: Request):
    user_data = await require_auth(request)
    data = await request.json()
    items = data.get("items")
    amount = data.get("amount")
    address = data.get("address")
    
    if not items or amount is None or not address:
        return JSONResponse({"success": False, "message": "Missing order details"})
        
    db = get_database()
    
    new_order = {
        "userId": user_data["user_id"],
        "items": items,
        "amount": amount,
        "address": address,
        "status": "Food Processing",
        "date": datetime.datetime.utcnow(),
        "payment": False
    }
    
    result = await db.orders.insert_one(new_order)
    order_id = str(result.inserted_id)
    
    # Mock Payment Logic
    # In a real app, you would integrate Stripe here
    # Since we're doing "mock payment", we redirect to a mock success URL
    
    # Clear cart after placing order
    await db.users.update_one(
        {"_id": ObjectId(user_data["user_id"])},
        {"$set": {"cartData": {}}}
    )
    
    # Simulate a Stripe session URL (mock)
    mock_session_url = f"/api/order/verify?success=true&orderId={order_id}"
    
    return JSONResponse({"success": True, "session_url": mock_session_url})

@router.get("/verify")
async def verify_order(orderId: str, success: bool):
    db = get_database()
    if success:
        await db.orders.update_one({"_id": ObjectId(orderId)}, {"$set": {"payment": True}})
        return JSONResponse({"success": True, "message": "Paid"})
    else:
        await db.orders.delete_one({"_id": ObjectId(orderId)})
        return JSONResponse({"success": False, "message": "Not Paid"})

@router.get("/userorders")
async def user_orders(request: Request):
    user_data = await require_auth(request)
    db = get_database()
    orders = await db.orders.find({"userId": user_data["user_id"]}).sort("date", -1).to_list(length=100)
    
    order_list = []
    for order in orders:
        order_list.append({
            "id": str(order["_id"]),
            "items": order["items"],
            "amount": order["amount"],
            "status": order["status"],
            "payment": order["payment"],
            "date": order["date"].isoformat()
        })
    return JSONResponse({"success": True, "data": order_list})
