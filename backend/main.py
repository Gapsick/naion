from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import chat, summary, auth, dev
from routes import records

app = FastAPI(title="内音 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router,    prefix="/api/auth",    tags=["auth"])
app.include_router(chat.router,    prefix="/api/chat",    tags=["chat"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(dev.router,     prefix="/api/dev",     tags=["dev"])

@app.get("/")
def root():
    return {"status": "ok", "app": "内音"}
