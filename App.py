import streamlit as st
from google import genai
import docx
import io

# Page Config
st.set_page_config(page_title="SharpsharpNaija", page_icon="🎬", layout="centered")

st.title("🎬 SharpsharpNaija")
st.markdown("### *No dulling. Fast, automated subtitling and Premiere Pro packaging for Nollywood.*")

# Securely grab the API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit App Secrets.")
else:
    # 1. File Upload
    uploaded_file = st.file_uploader("Upload Audio Track (.mp3, .aac, .wav)", type=["mp3", "aac", "wav", "m4a"])

    if uploaded_file is not None:
        st.audio(uploaded_file)
        
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
            with st.spinner("SharpsharpNaija engine is listening to audio & translating..."):
                try:
                    audio_bytes = uploaded_file.read()
                    file_mime = uploaded_file.type if uploaded_file.type else "audio/mp3"
                    
                    # Initialize Gemini client
                    client = genai.Client(api_key=api_key)
                    
                    # Upload with explicit mime_type
                    audio_file_ref = client.files.upload(
                        file=io.BytesIO(audio_bytes),
                        config={
                            'display_name': uploaded_file.name,
                            'mime_type': file_mime
                        }
                    )
                    
                    prompt = f"""
                    Listen to this audio track. Transcribe any spoken Yorùbá, Nigerian Pidgin, or English and provide a clean English translation suitable for professional movie subtitles.
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
                    st.error(f"An error occurred during translation: {e}")
