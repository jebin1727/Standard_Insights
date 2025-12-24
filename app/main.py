from fastapi import FastAPI
from app.api.router import router

app = FastAPI(title="Natural Language Analytics Interface")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
