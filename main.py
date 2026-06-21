from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import time
import os

# Initialize the FastAPI app
app = FastAPI(title="Chirper Backend API")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    text: str

# --- LOAD THE KNOWLEDGE BASE ---
# This opens the JSON file you just created and loads it into Python's memory
try:
    with open("intents.json", "r") as file:
        intents_data = json.load(file)
except Exception as e:
    intents_data = {"intents": []}
    print(f"Error loading memory: {e}")

# --- THE CHAT ENDPOINT & NLP LOGIC ---
@app.post("/api/chat")
async def chat_endpoint(message: UserMessage):
    user_text = message.text.lower()
    time.sleep(0.5) # Slight delay to feel human
    
    # Default fallback if the bot doesn't understand at all
    fallback_message = "I am still learning the Ed John IMT campus rules. Could you rephrase your question, or contact the admin?"
    best_response = fallback_message
    highest_match_score = 0

    # --- THE MATCHING ENGINE ---
    # We loop through every category in your JSON file
    for intent in intents_data.get("intents", []):
        for pattern in intent.get("patterns", []):
            pattern_lower = pattern.lower()
            
            # 1. Check for a direct substring match
            if pattern_lower in user_text or user_text in pattern_lower:
                best_response = random.choice(intent["responses"])
                highest_match_score = 100
                break
                
            # 2. Check for word overlaps (Basic NLP tokenization)
            pattern_words = set(pattern_lower.split())
            user_words = set(user_text.split())
            match_count = len(pattern_words.intersection(user_words))
            
            # If this pattern has more matching words than the last one, it becomes the new best guess
            if match_count > highest_match_score:
                highest_match_score = match_count
                best_response = random.choice(intent["responses"])

        # Stop looking if we found a perfect 100% match
        if highest_match_score == 100:
            break

    # If no words matched at all, it will return the fallback_message
    if highest_match_score == 0:
        return {"reply": fallback_message}

    return {"reply": best_response}
