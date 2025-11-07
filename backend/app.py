from fastapi import FastAPI
from routes.transactions_route import router as transactions_router

app = FastAPI()

app.include_router(transactions_router)

@app.get("/")
def entrypoint():
    return {"message": "Hello, World!"}

