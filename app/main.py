from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Import router baru (ranking) di sini
from .routers import auth, profile, preference, qdss, fuzzy_inference, ruleset, ranking
from .seeder import run_seeders

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("test")
    # run_seeders() # Matikan jika tidak perlu seed ulang setiap restart
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/expert/profile", tags=["profile"])
app.include_router(preference.router, prefix="/expert/preference", tags=["preference"])
app.include_router(qdss.router, prefix="/qdss", tags=["QDSS"])
app.include_router(ruleset.router, prefix="/ruleset", tags=["ruleset"])
app.include_router(fuzzy_inference.router, prefix="/inference", tags=["fuzzy-inference"])

# Register Router Ranking
app.include_router(ranking.router, prefix="/expert/ranking", tags=["ranking"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Auth"}