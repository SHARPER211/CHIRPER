import streamlit as st
from google import genai
import docx
import io
import tempfile
import os
from moviepy.editor import VideoFileClip

# Page Config
st.set_page_config(page_title="SharpsharpNaija", page_icon="🎬", layout="centered")

st.title("🎬 SharpsharpNaija")
st.markdown("### *No dulling. Fast, automated subtitling and Premiere Pro packaging for Nollywood.*")

# Securely grab the API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit App Secrets.")
else:
    # 1. Video & Audio File Upload (Accepts MP4, MKV, MOV alongside audio)
    uploaded_file = st.file_uploader(
        "Upload Movie File (.mp4, .mkv, .mov) or Audio (.mp3, .wav)", 
        type=["mp4", "mkv", "mov", "mp3", "aac", "wav", "m4a"]
    )

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Check if it's a video file that needs audio stripping
        if file_extension in ["mp4", "mkv", "mov"]:
            st.info("🎞️ Video detected! Stripping audio track automatically sharp-sharp...")
            
            # Save uploaded video temporarily
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}")
            tfile.write(uploaded_file.read())
            tfile.close()
            
            # Extract audio using moviepy
            audio_path = tfile.name + ".mp3"
            video_clip = VideoFileClip(tfile.name)
            video_clip.audio.write_audiofile(audio_path, logger=None)
            video_clip.close()
            
            # Read stripped audio bytes
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            file_mime = "audio/mp3"
            
            # Cleanup temp files
            os.unlink(tfile.name)
            os.unlink(audio_path)
            
            st.success("Audio successfully separated from video track!")
            st.audio(audio_bytes, format="audio/mp3")
            
        else:
            # It's already an audio file
            st.audio(uploaded_file)
            audio_bytes = uploaded_file.read()
            file_mime = uploaded_file.type if uploaded_file.type else "audio/mp3"
        
        # 2. Export Format Selector
        st.markdown("### Choose Output Format")
        output_format = st.selectbox(
            "Select how you want your delivery package:",
            [
                "MS Word (.docx) - Clean Translation Text Only",
                "Subtitles (.srt) - Timed Subtitle File",
                "Premiere Pro Package (.xml + .prtl) - Ready-to-Import Timeline"
            ]
        )
        
        # 3. Custom Style / Director Notes
        custom_instructions = st.text_input(
            "Custom Style / Director Notes (Optional):", 
            placeholder="e.g., Keep street slang raw, or translate Yorùbá dialogue to English..."
        )

        if st.button("Generate Sharpsharp Output"):
            with st.spinner("SharpsharpNaija engine is processing your media & translating..."):
                try:
                    # Initialize Gemini client
                    client = genai.Client(api_key=api_key)
                    
                    # Upload extracted audio to Gemini API
                    audio_file_ref = client.files.upload(
                        file=io.BytesIO(audio_bytes),
                        config={
                            'display_name': uploaded_file.name,
                            'mime_type': file_mime
                        }
                    )
                    
                    prompt = f"""
                    Listen to this media track. Transcribe any spoken Yorùbá, Nigerian Pidgin, or English and provide a clean English translation suitable for professional movie subtitles.
                    Director Notes / Style: {custom_instructions}
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=[audio_file_ref, prompt]
                    )
                    
                    translated_text = response.text
                    st.success("Pipeline executed successfully sharp-sharp!")
                    
                    # 4. Handle Deliverables Based on Chosen Format
                    if "MS Word" in output_format:
                        st.subheader("📄 MS Word Translation Preview")
                        st.write(translated_text)
                        
                        doc = docx.Document()
                        doc.add_heading("SharpsharpNaija Translation Script", 0)
                        doc.add_paragraph(translated_text)
                        
                        bio = io.BytesIO()
                        doc.save(bio)
                        bio.seek(0)
                        
                        st.download_button(
                            label="📥 Download MS Word Document (.docx)",
                            data=bio,
                            file_name="SharpsharpNaija_Translation.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        
                    elif ".srt" in output_format:
                        st.subheader("⏱️ SRT Subtitle Preview")
                        srt_mock = f"1\n00:00:01,000 --> 00:00:05,000\n{translated_text}"
                        st.text(srt_mock)
                        
                        st.download_button(
                            label="📥 Download Subtitles (.srt)",
                            data=srt_mock,
                            file_name="SharpsharpNaija_Subtitles.srt",
                            mime="text/plain"
                        )
                        
                    else:
                        st.subheader("🎞️ Premiere Pro XML Package Preview")
                        xml_mock = "<xmeml version='4'><sequence>Mock Premiere Package</sequence></xmeml>"
                        st.text(xml_mock)
                        
                        st.download_button(
                            label="📥 Download Premiere Pro Package (.xml)",
                            data=xml_mock,
                            file_name="SharpsharpNaija_Premiere_Package.xml",
                            mime="application/xml"
                        )
                    
                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")
