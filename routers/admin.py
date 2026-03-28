from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from config.database import get_database
from middleware.auth import require_admin
from bson import ObjectId

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/listorders")
async def list_orders(request: Request):
    await require_admin(request)
    db = get_database()
    orders = await db.orders.find({}).sort("date", -1).to_list(length=200)
    
    order_list = []
    for order in orders:
        order_list.append({
            "id": str(order["_id"]),
            "items": order["items"],
            "amount": order["amount"],
            "status": order["status"],
            "payment": order["payment"],
            "address": order["address"],
            "date": order["date"].isoformat()
        })
    return JSONResponse({"success": True, "data": order_list})

@router.post("/status")
async def update_status(request: Request):
    await require_admin(request)
    data = await request.json()
    order_id = data.get("orderId")
    status = data.get("status")
    
    if not order_id or not status:
        return JSONResponse({"success": False, "message": "Order ID and status are required"})
        
    db = get_database()
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status}}
    )
    return JSONResponse({"success": True, "message": "Status Updated Successfully"})
