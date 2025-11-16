from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, profile, preference, qdss
from .seeder import run_seeders

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("test")
    run_seeders()
    
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust as needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/expert/profile", tags=["profile"])
app.include_router(preference.router, prefix="/expert/preference", tags=["preference"])
app.include_router(qdss.router, prefix="/qdss", tags=["QDSS"])


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Auth"}