from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.transactions_route import router as transactions_router
from routes.token_route import router as token_router
from routes.db_route import router as db_router
from routes.auth_route import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(transactions_router)
app.include_router(token_router)

#put db_router to .post before prod
app.include_router(db_router)
app.include_router(auth_router)

@app.get("/")
def entrypoint():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)