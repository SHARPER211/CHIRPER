import modal

# 1. Build the cloud computer (Installs our Python libraries and ffmpeg for audio)
image = (
    modal.Image.debian_slim()
    .apt_install("ffmpeg")
    .pip_install_from_requirements("requirements.txt")
)

app = modal.App("sharpsharp-naija-backend")

# 2. Wrap our pipeline into a web API endpoint running on an Nvidia T4 GPU
@app.function(
    image=image, 
    gpu="T4", 
    timeout=3600, # 1-hour timeout for long Nollywood movies
    secrets=[modal.Secret.from_name("gemini-api-key")]
)
@modal.web_endpoint(method="POST")
def api_translate(audio_url: str):
    """
    This is the live URL your frontend website will hit.
    When a user clicks generate, the frontend sends the audio_url here.
    """
    # Later, we will add the 3 lines of code here to download the audio_url 
    # and pass it to our run_pipeline() function from main.py.
    return {"status": "SharpSharpNaija Backend is Live! Ready for frontend connection."}
