import streamlit as st
from google import genai
from google.genai import types
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io

# 1. Page Config
st.set_page_config(page_title="Clinic AI Assistant", page_icon="🏥", layout="wide")

# 2. Sidebar - Lead Collection
st.sidebar.title("📌 Bookings & Leads")
st.sidebar.caption("ഉപഭോക്താക്കളുടെ വിവരങ്ങൾ ഇവിടെ കാണാം")

if "leads" not in st.session_state:
    st.session_state.leads = []

# 3. Main Title
st.title("🏥 City Health Clinic - AI Assistant")
st.caption("24/7 Multi-lingual Voice & Text Support")

# 4. Gemini Client (നിങ്ങളുടെ API Key നൽകുക)
client = genai.Client(api_key="GEMINI_API_KEY")

# 5. Clinic Data വായിക്കുന്നു
@st.cache_data
def load_clinic_info():
    with open("clinic_data.txt", "r", encoding="utf-8") as file:
        return file.read()

clinic_info = load_clinic_info()

# 6. System Prompt
system_instruction = f"""
You are a helpful and polite customer support assistant for City Health Clinic.
Answer the user's questions based ONLY on the provided clinic details below.

CRITICAL INSTRUCTION FOR LANGUAGE & LEADS:
- Provide every answer in BOTH English and Malayalam.
- First write the answer in English clearly, then in Malayalam.
- Keep responses short and concise so that text-to-speech sounds natural.
- If requested information is missing, inform them politely and suggest contacting the clinic directly.

Clinic Details:
{clinic_info}
"""

# 7. Sidebar Form
# 7. Sidebar Booking Form & Lead Display
with st.sidebar.expander("📅 Book Appointment Directly", expanded=False):
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Name / പേര്")
        phone = st.text_input("Phone Number / ഫോൺ നമ്പർ")
        submit_button = st.form_submit_button("Submit / സമർപ്പിക്കുക")
        
        if submit_button:
            if name and phone:
                st.session_state.leads.append({"Name": name, "Phone": phone})
                st.success("Details saved! / വിവരങ്ങൾ ശേഖരിച്ചു!")
            else:
                st.warning("Please fill all fields")

# ശേഖരിച്ച വിവരങ്ങൾ (പേരും ഫോൺ നമ്പറും) സൈഡ്ബാറിൽ കാണിക്കാൻ
if st.session_state.leads:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Recent Patient Leads")
    for lead in st.session_state.leads:
        st.sidebar.write(f"👤 **{lead['Name']}**")
        st.sidebar.write(f"📞 {lead['Phone']}")
        st.sidebar.write("---")

# 8. Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to City Health Clinic AI Assistant! / City Health Clinic AI അസിസ്റ്റന്റിലേക്ക് സ്വാഗതം!"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Voice Input ഓപ്ഷൻ
st.write("🎙️ **സംസാരിച്ച് ചോദ്യം ചോദിക്കാൻ മൈക്ക് അമർത്തുക:**")
voice_text = speech_to_text(language='ml-IN', start_prompt="🎤 Speak Now", stop_prompt="⏹️ Stop", key='voice_input')

# Text അല്ലെങ്കിൽ Voice വഴി വരുന്ന ഇൻപുട്ട് പ്രോസസ്സ് ചെയ്യാൻ
text_prompt = st.chat_input("Ask a question / ചോദ്യങ്ങൾ ചോദിക്കൂ...")

prompt = voice_text if voice_text else text_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing... / ചിന്തിക്കുന്നു..."):
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            ai_reply = response.text
            st.markdown(ai_reply)

            # Text to Speech ഓഡിയോ പ്ലെയർ നൽകുന്നു
            try:
                tts = gTTS(text=ai_reply, lang='ml')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp, format='audio/mp3')
            except Exception as e:
                pass
    
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
