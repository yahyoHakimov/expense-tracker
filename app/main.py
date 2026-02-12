from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app import models
from app.database import engine
from app.routers import auth, expenses
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Expense Tracker API",
    description="Track your expenses with authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(expenses.router)

# Serve frontend
@app.get("/")
def root():
    return FileResponse('frontend/index.html')

# Mount static files
if os.path.exists('frontend'):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")