import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# Create required directories
Path("uploads/food").mkdir(parents=True, exist_ok=True)
Path("static/css").mkdir(parents=True, exist_ok=True)
Path("static/js").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from config.database import connect_to_mongo, close_mongo_connection
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(title="TOMATO - Food Delivery", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
from routers import auth, food, cart, order, admin as admin_router

app.include_router(auth.router)
app.include_router(food.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(admin_router.router)


# ── Page Routes ──────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})


@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})


@app.get("/checkout/success", response_class=HTMLResponse)
async def checkout_success(request: Request):
    return templates.TemplateResponse("checkout_success.html", {"request": request})
