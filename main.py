import os  # <-- This new import lets Python read hidden files
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

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

# --- CONFIGURE THE LLM SECURELY ---
# This pulls the key directly from Render's secret vault!
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 

# Initialize the Groq Client
client = Groq(api_key=GROQ_API_KEY)

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
        # Generate content using the blazing fast Llama 3 model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message.text,
                }
            ],
            model="llama3-8b-8192", 
        )
        
        return {"reply": chat_completion.choices[0].message.content}
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"reply": "Sorry, my AI core is currently offline. Please try again in a moment."}
