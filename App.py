import streamlit as st
from google import genai
from google.genai import types
import docx
import io
import json
import tempfile
import os

st.set_page_config(page_title="SharpsharpNaija", page_icon="🎬", layout="centered")

st.title("🎬 SharpsharpNaija")
st.markdown("### *No dulling. Fast, automated subtitling and Premiere Pro packaging for Nollywood.*")

api_key = st.secrets.get("GEMINI_API_KEY", "")
modal_url = st.secrets.get("MODAL_GPU_URL", "")  # Optional Serverless GPU endpoint

def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

def build_flagged_premiere_xml(subs: list, fps: int = 25) -> str:
    """Generates Premiere Pro XML where unsure/flagged lines turn YELLOW with timeline markers!"""
    clips_xml = ""
    markers_xml = ""
    for sub in subs:
        start_frame = int(round(sub["start"] * fps))
        end_frame = int(round(sub["end"] * fps))
        text = sub["english_subtitle"]
        needs_review = sub.get("needs_review", False)
        note = sub.get("review_note", "Check audio clarity")
        
        # Idea #3: Color-code unsure clips Yellow in Premiere Pro, confident clips Violet!
        color_label = "Yellow" if needs_review else "Violet"
        prefix = "[CHECK] " if needs_review else ""
        
        clips_xml += f"""
        <clipitem id="subtitle_{sub['id']}">
            <name>{prefix}{text[:28]}</name>
            <enabled>TRUE</enabled>
            <start>{start_frame}</start>
            <end>{end_frame}</end>
            <labels><label2>{color_label}</label2></labels>
        </clipitem>"""
        
        if needs_review:
            markers_xml += f"""
            <marker>
                <name>⚠️ Review Subtitle #{sub['id']}</name>
                <comment>Heard: {sub.get('yoruba_heard', '')} | Note: {note}</comment>
                <in>{start_frame}</in>
                <out>-1</out>
            </marker>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
    <sequence>
        <name>SharpsharpNaija_Subtitled_Seq</name>
        <rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
        {markers_xml}
        <media><video><track>{clips_xml}</track></video></media>
    </sequence>
</xmeml>"""

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please add it to your Streamlit App Secrets.")
else:
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

    human_script = st.file_uploader("Upload Human Translation Script (Optional - .txt or .docx)", type=["txt", "docx"])

    # Idea #2: Built-in Cultural Glossary & Memory Bank
    with st.expander("📚 Cultural Glossary & Nollywood Rules (Idea #2 - Auto-Applied)"):
        glossary_rules = st.text_area(
            "Words, Names & Cultural Tags the AI Must Respect:",
            value=(
                "- When actors chant deep family praise poetry (Oríkì), format as: <Chanting Panegyrics>\n"
                "- When an Ifá priest chants verses, format as: <Chanting Ifa incantations>\n"
                "- Keep character names & titles intact (e.g., Bàbá Qudus, Ṣòbòtò, Oga, Kabiyesi).\n"
                "- Never translate Yorùbá idioms word-for-word; translate the dramatic intent."
            ),
            height=110
        )

    # Idea #3: Confidence Flagging Options for SRT & XML
    flag_in_files = st.checkbox(
        "🔍 Mark unsure/mumbled lines inside .SRT (`[⚠️ CHECK]`) and Premiere .XML (Yellow Clips + Markers)", 
        value=True
    )

    output_format = st.selectbox(
        "Select your delivery package:",
        [
            "Subtitles (.srt) - Timed Subtitle File",
            "Premiere Pro Package (.xml) - Color-Coded Timeline with Review Markers",
            "MS Word (.docx) - Clean Translation Script + Review Notes"
        ]
    )
    
    custom_instructions = st.text_input(
        "Custom Style / Director Notes (Optional):", 
        placeholder="e.g., Keep street slang raw, match professional broadcast tone..."
    )

    if st.button("Generate Sharpsharp Output"):
        if not media_source or isinstance(media_source, str):
            st.warning("⚠️ Please upload an audio/video clip to test the live VAD + Native Ear pipeline!")
        else:
            progress_bar = st.progress(10)
            status_text = st.empty()
            status_text.text("🚀 Preparing media & locking speech timestamps...")
            
            try:
                from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
                
                ext = media_source.name.split(".")[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                    tmp.write(media_source.read())
                    tmp_path = tmp.name

                # Run Silero VAD to strip silence and get exact timestamps
                vad_model = load_silero_vad()
                wav = read_audio(tmp_path, sampling_rate=16000)
                speech_ts = get_speech_timestamps(
                    wav, vad_model, sampling_rate=16000,
                    min_speech_duration_ms=250, min_silence_duration_ms=350, return_seconds=True
                )
                vad_slots = [{"id": i+1, "start": round(t["start"], 2), "end": round(t["end"], 2)} for i, t in enumerate(speech_ts)]
                
                progress_bar.progress(50)
                status_text.text(f"⚡ Found {len(vad_slots)} spoken dialogue lines! Running Native Ear Double-Take...")

                client = genai.Client(api_key=api_key)
                uploaded_ref = client.files.upload(
                    file=tmp_path,
                    config={"display_name": media_source.name, "mime_type": media_source.type or "audio/mp3"}
                )

                prompt = f"""
                Listen to this Nigerian movie audio and align strictly to these {len(vad_slots)} Silero VAD speech slots:
                {json.dumps(vad_slots)}

                CULTURAL GLOSSARY (MUST FOLLOW):
                {glossary_rules}

                NATIVE EAR DOUBLE-TAKE:
                1. First hear the raw Yorùbá/Pidgin/English in each slot.
                2. Question yourself against the scene context so you never write nonsense.
                3. Set "needs_review": true ONLY if the audio is mumbled, noisy, or uncertain (<85% confidence), and write a brief "review_note".

                Return ONLY a JSON list of objects with keys:
                "id" (int), "start" (float), "end" (float), "yoruba_heard" (str), "english_subtitle" (str), "needs_review" (bool), "review_note" (str).
                Director Note: {custom_instructions}
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[uploaded_ref, prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                os.unlink(tmp_path)

                subs = json.loads(response.text)
                progress_bar.progress(100)
                status_text.text("✅ Done sharp-sharp!")

                # Show Confidence Heatmap Summary right in the browser!
                flagged = [s for s in subs if s.get("needs_review")]
                if flagged:
                    st.warning(f"⚠️ **Confidence Heatmap:** {len(flagged)} of {len(subs)} lines were flagged for quick human review:")
                    for f_sub in flagged:
                        st.markdown(
                            f"- **Line #{f_sub['id']} ({format_srt_time(f_sub['start'])})**: "
                            f"*\"{f_sub['english_subtitle']}\"* — **Why:** {f_sub.get('review_note', 'Verify audio')} "
                            f"*(Heard: `{f_sub.get('yoruba_heard', '')}`)*"
                        )
                else:
                    st.success(f"🎯 100% High Confidence across all {len(subs)} dialogue lines!")

                # Export Deliverables
                if ".srt" in output_format:
                    srt_lines = []
                    for s in subs:
                        tag = "[⚠️ CHECK] " if (flag_in_files and s.get("needs_review")) else ""
                        srt_lines.append(
                            f"{s['id']}\n{format_srt_time(s['start'])} --> {format_srt_time(s['end'])}\n{tag}{s['english_subtitle']}\n"
                        )
                    srt_final = "\n".join(srt_lines)
                    st.subheader("⏱️ Timed SRT Preview")
                    st.text_area("SRT Output", srt_final, height=250)
                    st.download_button("📥 Download Subtitles (.srt)", srt_final, "SharpsharpNaija.srt", "text/plain")

                elif ".xml" in output_format:
                    xml_final = build_flagged_premiere_xml(subs)
                    st.subheader("🎞️ Color-Coded Premiere Pro XML Preview")
                    st.info("💡 Confident subtitles are labeled Violet. Flagged subtitles are labeled YELLOW with Timeline Markers!")
                    st.download_button("📥 Download Premiere XML (.xml)", xml_final, "SharpsharpNaija_Timeline.xml", "application/xml")

                else:
                    doc = docx.Document()
                    doc.add_heading("SharpsharpNaija Translation Script", 0)
                    for s in subs:
                        prefix = "⚠️ [NEEDS REVIEW] " if (flag_in_files and s.get("needs_review")) else ""
                        doc.add_paragraph(f"[{format_srt_time(s['start'])}] {prefix}{s['english_subtitle']}")
                    bio = io.BytesIO()
                    doc.save(bio)
                    bio.seek(0)
                    st.download_button("📥 Download Word Script (.docx)", bio, "SharpsharpNaija_Script.docx")

            except Exception as e:
                st.error(f"Processing error: {e}")
