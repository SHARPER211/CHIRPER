from vad_asr import transcribe_with_vad
from gemini_engine import generate_show_bible, translate_subtitles
from exporters import generate_srt, generate_premiere_xml

def run_pipeline(audio_file_path, output_name="Final_Movie"):
    print("Step 1: Running Silero VAD and NaijaVox ASR...")
    asr_chunks = transcribe_with_vad(audio_file_path)
    
    print("Step 2: Gemini generating Cinematic Context (Show Bible)...")
    # Combine the text to feed to the Show Bible prompt
    raw_text = " ".join([chunk["text"] for chunk in asr_chunks])
    show_bible = generate_show_bible(raw_text)
    
    print("Step 3: Gemini performing Contextual Translation...")
    translated_chunks = translate_subtitles(asr_chunks, show_bible)
    
    if not translated_chunks:
        print("Translation failed. Exiting.")
        return
        
    print("Step 4: Exporting final files...")
    
    # Export SRT
    srt_content = generate_srt(translated_chunks)
    with open(f"{output_name}.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)
        
    # Export Premiere Pro XML
    xml_content = generate_premiere_xml(translated_chunks, sequence_name=output_name)
    with open(f"{output_name}.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    print(f"Success! Translation exported as {output_name}.srt and {output_name}.xml")

if __name__ == "__main__":
    # This is where the uploaded file will be passed in
    audio_input = "sample_audio.wav" 
    run_pipeline(audio_input)
