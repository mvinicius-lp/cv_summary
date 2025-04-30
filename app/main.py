from fastapi import FastAPI
from app.routes import  cv_summary

app = FastAPI()

app.include_router(cv_summary.router)