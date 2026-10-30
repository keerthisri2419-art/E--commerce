import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import seed_database
from routers import products, orders, ai, payments

# Load environment variables from the root folder
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(dotenv_path)

app = FastAPI(
    title="E-com API",
    description="FastAPI Backend for the E-com platform, integrated with Firestore and Firebase Auth",
    version="1.0.0"
)

# Configure CORS Middleware to allow requests from the React frontend (running on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production, e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints under /api
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(payments.router, prefix="/api")

@app.on_event("startup")
def startup_event():
    print("FastAPI server starting up...")
    # Initialize and seed database if empty
    seed_database()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the E-com FastAPI Backend Service",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
