from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from config.database import get_database
from middleware.auth import create_token

router = APIRouter(prefix="/auth", tags=["auth"])
# Use pbkdf2_sha256 for maximum compatibility and no string length limits
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@router.post("/register")
async def register(request: Request):
    try:
        data = await request.json()
        print(f"Registration request received for: {data.get('email')}")
        
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not all([name, email, password]):
            return JSONResponse({"success": False, "message": "All fields are required"})
        
        # Bcrypt has a 72-byte limit. We truncate it to avoid the server error.
        print(f"Password length received: {len(password)}")
        password = password[:72] 

        if len(password) < 8:
            return JSONResponse({"success": False, "message": "Password must be at least 8 characters"})
        if "@" not in email:
            return JSONResponse({"success": False, "message": "Please enter a valid email address"})

        db = get_database()
        if db is None:
            print("❌ Error: Database connection is not ready!")
            return JSONResponse({"success": False, "message": "Database not ready. Please wait a moment."})
            
        existing = await db.users.find_one({"email": email})
        if existing:
            return JSONResponse({"success": False, "message": "User already exists with this email"})

        hashed = pwd_context.hash(password)
        user_doc = {
            "name": name,
            "email": email,
            "password": hashed,
            "role": "user",
            "cartData": {},
        }
        result = await db.users.insert_one(user_doc)
        token = create_token(str(result.inserted_id), "user")

        response = JSONResponse({"success": True, "message": "Account created successfully!", "role": "user"})
        response.set_cookie("access_token", token, httponly=True, max_age=604800, samesite="lax")
        print(f"✅ User registered: {email}")
        return response
    except Exception as e:
        print(f"❌ Registration Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "message": f"Server Error: {str(e)}"}, status_code=500)


@router.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    db = get_database()
    user = await db.users.find_one({"email": email})
    if not user:
        return JSONResponse({"success": False, "message": "No account found with this email"})
    if not pwd_context.verify(password, user["password"]):
        return JSONResponse({"success": False, "message": "Incorrect password"})

    token = create_token(str(user["_id"]), user.get("role", "user"))

    response = JSONResponse({
        "success": True,
        "message": "Welcome back!",
        "role": user.get("role", "user"),
        "name": user["name"],
    })
    response.set_cookie("access_token", token, httponly=True, max_age=604800, samesite="lax")
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse({"success": True, "message": "Logged out"})
    response.delete_cookie("access_token")
    return response


@router.get("/me")
async def me(request: Request):
    from middleware.auth import get_current_user
    from bson import ObjectId

    user_data = await get_current_user(request)
    if not user_data:
        return JSONResponse({"success": False, "authenticated": False})

    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_data["user_id"])})
    if not user:
        return JSONResponse({"success": False, "authenticated": False})

    return JSONResponse({
        "success": True,
        "authenticated": True,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "cartData": user.get("cartData", {}),
        },
    })
