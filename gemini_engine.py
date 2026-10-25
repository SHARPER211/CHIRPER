import google.generativeai as genai
import os
import json

# Initialize Gemini API
# Make sure to set your API key in your environment variables: export GEMINI_API_KEY="your_key"
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_show_bible(raw_asr_text):
    """
    Pass 1: The Context Engine. 
    Reads the raw transcript and builds the cinematic context map.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are a master film critic analyzing a rough Nollywood ASR transcript. 
    Do not translate the text. Read it and output a JSON 'Show Bible' containing:
    1. "synopsis": A brief summary of the plot.
    2. "characters": A list of identified characters and their relationships.
    3. "tone": The emotional vibe (e.g., comic, tense drama, historical).
    
    Raw ASR Transcript:
    {raw_asr_text}
    """
    
    response = model.generate_content(prompt)
    # In production, we parse the JSON. For now, we return the raw string.
    return response.text

def translate_subtitles(asr_chunks, show_bible):
    """
    Pass 2: The Master Translator.
    Applies the SharpSharpNaija Style Guide to contextually translate the chunks.
    """
    
    # This System Instruction is the exact logic extracted from your boss's workflow
    system_instruction = f"""
    You are the elite Master Translator for SharpSharpNaija. Your job is to translate Yorùbá, 
    Nigerian Pidgin, and Nigerian English ASR transcripts into cinematic English subtitles.
    
    MOVIE CONTEXT (SHOW BIBLE):
    {show_bible}
    
    TRANSLATION PHILOSOPHY:
    1. Translate communicative intent (threat, joke, blessing), not just literal vocabulary.
    2. Preserve the social relationship (e.g., retain "Old one", "My in-law", "Madam" when socially relevant).
    3. Translate the emotional effect. E.g., "What kind of nonsense is this?" should retain its confrontational force.
    
    CULTURAL GLOSSARY & IDIOMS:
    - "God forbid" -> Retain as an expression of rejection.
    - "It shall be well with you" -> Retain as a blessing/reassurance.
    - "Well-done" -> Translate based on context (greeting vs. praise).
    - "Bad mouth" -> Translate the accusation naturally but retain the confrontational tone.
    
    PERFORMANCE TAGGING RULES (STRICT):
    - Use <Chanting panegyrics> ONLY for incantations, charms, or wordplay invoking spirits.
    - Use <Ancestral praise> or <Eulogizing> for praising a person, lineage, or ruler.
    - Use <Singing> for songs without transcribing lyrics, UNLESS the lyrics are critical to the plot.
    - Use <Sulking> when a character is crying.
    
    DISCARD RULES (CRITICAL):
    - DISCARD all hissing sounds completely. Do not output <Hisses>.
    - DISCARD repetitive non-verbal cues that do not advance the plot.
    - DISCARD random modern internet ad-libs if they break the immersion of the scene.
    
    INSTRUCTIONS:
    I will provide you with a JSON list of timestamped ASR chunks. 
    Return the translated chunks in the exact same JSON format, keeping the timestamps identical, 
    but replacing the 'text' field with your contextual English translation.
    """
    
    model = genai.GenerativeModel(
        model_name='gemini-3.5 flash-lite',
        system_instruction=system_instruction
    )
    
    # We pass the chunks as a stringified JSON to Gemini
    prompt = f"Here are the ASR chunks to translate:\
    n{json.dumps(asr_chunks)}"
    
    response = model.generate_content(prompt)
    
    # Clean and parse the returned JSON
    try:
        translated_chunks = json.loads(response.text.strip('```json').strip('```'))
        return translated_chunks
    except json.JSONDecodeError:
        print("Error: Gemini did not return valid JSON.")
        return []
