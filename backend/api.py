"""
Backend API routes.

This module exposes HTTP endpoints that the frontend uses to
communicate with the chatbot.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.chatbot import answer_question

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://2300-chatbat.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message" : "ECE2300 chatbot API is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    return answer_question(request.question)
