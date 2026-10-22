import streamlit as st
from google import genai

# Page Config
st.set_page_config(page_title="SharpsharpNaija", page_icon="🎬", layout="centered")

st.title("🎬 SharpsharpNaija")
st.markdown("### *No dulling. Fast, automated subtitling and Premiere Pro packaging for Nollywood.*")

# Securely grab the AQ. key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit App Secrets.")
else:
    uploaded_file = st.file_uploader("Upload Audio Track (.mp3 or .aac)", type=["mp3", "aac", "wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file)

        if st.button("Generate Sharpsharp Subtitles"):
            with st.spinner("SharpsharpNaija engine is processing audio & translating..."):
                try:
                    # Initialize Gemini client with verified model
                    client = genai.Client(api_key=api_key)

                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents="Verify system connection and translate sample: 'Ẹ kàárọ̀ o' to English."
                    )

                    st.success("Pipeline executed successfully sharp-sharp!")
                    st.write("**Gemini Output Test:**", response.text)

                except Exception as e:
                    st.error(f"An error occurred: {e}")
