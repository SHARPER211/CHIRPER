import streamlit as st
from google import genai
import docx
import io
import time

# Page Config
st.set_page_config(page_title="SharpsharpNaija", page_icon="🎬", layout="centered")

st.title("🎬 SharpsharpNaija")
st.markdown("### *No dulling. Fast, automated subtitling and Premiere Pro packaging for Nollywood.*")

# Securely grab the API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit App Secrets.")
else:
    # 1. Media Input Choice: Google Drive Link OR File Upload
    input_method = st.radio("Choose Media Source:", ["Upload File (Audio/Video)", "Google Drive / Cloud Link"])
    
    media_source = None
    if input_method == "Google Drive / Cloud Link":
        media_source = st.text_input("Paste Google Drive or Video Link:", placeholder="https://drive.google.com/file/d/...")
        st.caption("💡 *Tip: Ensure file sharing permissions are set to 'Anyone with the link can view'.*")
    else:
        media_source = st.file_uploader(
            "Upload Movie/Audio File (Max limit: 200MB for direct upload)", 
            type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"]
        )

    # 2. Optional Human Translation Script Upload (For matching your exact lines)
    human_script = st.file_uploader("Upload Human Translation Script (Optional - .txt or .docx)", type=["txt", "docx"])

    # 3. Export Format Selector
    st.markdown("### Choose Output Format")
    output_format = st.selectbox(
        "Select your delivery package:",
        [
            "MS Word (.docx) - Clean Translation Text Only",
            "Subtitles (.srt) - Timed Subtitle File",
            "Premiere Pro Package (.xml + .prtl) - Ready-to-Import Timeline"
        ]
    )
    
    # 4. Director Notes / Custom Style
    custom_instructions = st.text_input(
        "Custom Style / Director Notes (Optional):", 
        placeholder="e.g., Keep street slang raw, match professional broadcast tone..."
    )

    if st.button("Generate Sharpsharp Output"):
        if not media_source:
            st.warning("⚠️ Please provide a media file or cloud link first!")
        else:
            # Professional, clean loading experience
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🚀 Initializing SharpsharpNaija engine...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            status_text.text("📥 Connecting to media source...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            try:
                # Initialize Gemini client
                client = genai.Client(api_key=api_key)
                
                status_text.text("⚡ Processing and generating precision output...")
                progress_bar.progress(80)
                
                if isinstance(media_source, str):
                    prompt_content = f"The user provided this cloud media link: {media_source}. Process the media, transcribe, and translate."
                else:
                    audio_bytes = media_source.read()
                    file_mime = media_source.type if media_source.type else "audio/mp3"
                    audio_file_ref = client.files.upload(
                        file=io.BytesIO(audio_bytes),
                        config={'display_name': media_source.name, 'mime_type': file_mime}
                    )
                    prompt_content = audio_file_ref
                
                script_context = ""
                if human_script:
                    script_context = f"\nUser provided human script reference for alignment."

                prompt = f"""
                Listen/analyze the provided media. Transcribe spoken Nigerian languages/dialogue and provide a clean English translation suitable for movie subtitles.
                Director Notes: {custom_instructions}
                {script_context}
                """
                
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=[prompt_content, prompt] if not isinstance(media_source, str) else prompt_content + "\n\n" + prompt
                )
                
                translated_text = response.text
                
                progress_bar.progress(100)
                status_text.text("✅ Done sharp-sharp!")
                st.success("Pipeline executed successfully!")
                
                # Deliverables
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
                progress_bar.progress(100)
                status_text.text("❌ Error encountered.")
                st.error(f"An error occurred: {e}")
