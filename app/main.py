from fastapi import FastAPI
from app.routes import flights

app = FastAPI()

app.include_router(flights.router)
