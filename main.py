from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Initialize the FastAPI app
app = FastAPI(title="Chirper LLM Backend API")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

class UserMessage(BaseModel):
    text: str

# --- CONFIGURE THE LLM ---
GOOGLE_API_KEY = "AQ.Ab8RN6LLhsolW3xpGHoQPhzdDppDnXPIU8lgAKQDeDIH6Eu68g" 

# Initialize the modern SDK Client
client = genai.Client(api_key=GOOGLE_API_KEY)

# This System Prompt traps the LLM in character
system_prompt = """
You are Chirper, the official student support chatbot for Ed John Institute of Management and Technology (Ed John IMT).
Your personality is helpful, concise, and professional. 

Base campus rules you must know:
- Clearance: Handled at the main registry with printed files.
- School Fees: Must be generated as an invoice on the student portal.
- Portal Login Issues: Handled by ICT support via email.

If a student asks something completely unrelated to education, campus life, or school, politely decline to answer and remind them you are an academic assistant. Keep your responses short (1-3 sentences max) so they fit nicely in a chat widget.
"""

@app.post("/api/chat")
async def chat_endpoint(message: UserMessage):
    try:
        # Generate content using the modern library syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        
        return {"reply": response.text}
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"reply": "Sorry, my AI core is currently offline. Please try again in a moment."}
