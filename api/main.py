from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from auth_routes import router as auth_router
from cart_routes import router as cart_router
from order_routes import router as order_router

app = FastAPI(title="Shopping Cart API")

# Enable CORS for frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(router)
app.include_router(cart_router)
app.include_router(order_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
