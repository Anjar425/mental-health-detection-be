from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from .routers import auth, auth_me, profile, preference, qdss, fuzzy_inference, ruleset, ranking, admin, expert_groups
from .seeder import run_seeders

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("test")
    #run_seeders() # Matikan jika tidak perlu seed ulang setiap restart
    yield

app = FastAPI(lifespan=lifespan)

# Limit to known dev origins so credentialed requests (Authorization header) work properly.
# Using '*' with allow_credentials=True breaks CORS for credentialed requests in browsers.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(auth_me.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/expert/profile", tags=["profile"])
app.include_router(preference.router, prefix="/expert/preference", tags=["preference"])
app.include_router(qdss.router, prefix="/qdss", tags=["QDSS"])
app.include_router(ruleset.router, prefix="/ruleset", tags=["ruleset"])
app.include_router(fuzzy_inference.router, prefix="/inference", tags=["fuzzy-inference"])

# Register Router Ranking
app.include_router(ranking.router, prefix="/expert/ranking", tags=["ranking"])

# Register admin router

# Register admin router
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Register expert_groups router (admin only)
app.include_router(
    expert_groups.router,
    prefix="/admin/groups",
    tags=["Expert Groups"]
)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Auth"}