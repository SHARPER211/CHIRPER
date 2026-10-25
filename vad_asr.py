from faster_whisper import WhisperModel

def transcribe_with_vad(audio_file_path):
    """
    Strips silence using Silero VAD and transcribes speech using NaijaVox.
    """
    model_path = "Axiveri/NaijaVox-2.0-ct2" 
    model = WhisperModel(model_path, device="cuda", compute_type="float16")
    
    print("Chopping silence and transcribing...")
    
    segments, _ = model.transcribe(
        audio_file_path,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400, speech_pad_ms=150)
    )
    
    asr_chunks = []
    for segment in segments:
        asr_chunks.append({
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip()
        })
        
    return asr_chunks
