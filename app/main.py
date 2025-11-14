from fastapi import FastAPI
from .routers import auth, profile

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Auth"}