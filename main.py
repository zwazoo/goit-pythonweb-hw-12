from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from src.database.connection import get_db
from src.routers import auth, users, contacts

app = FastAPI()

origins = ["http://localhost", "http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded. Please try again later."},
    )


@app.get("/", name="Root")
async def root():
    return {"message": "Welcome to contacts API"}


@app.get("/health", name="Service health check")
async def get_health(db=Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if result.fetchone() is None:
            raise Exception("Database connection failed")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)
