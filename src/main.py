from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import users, auth, requisition
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get allowed origins from the .env file
allow_origins = os.getenv("ALLOW_ORIGINS", "").split(",")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Dynamically loaded origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(requisition.router_requisitions)
app.include_router(requisition.router_requisition_items)


