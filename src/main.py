from fastapi import FastAPI

from src.api import router


app = FastAPI(title="Finance Trackr API")
app.include_router(router)
