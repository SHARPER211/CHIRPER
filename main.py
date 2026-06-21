from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI(title="Chirper Backend API")

# Allow your GitHub Pages frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    text: str

@app.post("/api/chat")
async def chat_endpoint(message: UserMessage):
    user_text = message.text.lower()
    time.sleep(0.5)
    
    if "hi" in user_text or "hello" in user_text:
        bot_response = "Hello! Ed John IMT backend systems are officially online. What do you need help with?"
    elif "clearance" in user_text:
        bot_response = "To process your clearance, please visit the main registry with your printed files."
    else:
        bot_response = f"My NLP engine isn't fully trained yet. I heard you say: '{message.text}'"
        
    return {"reply": bot_response}
