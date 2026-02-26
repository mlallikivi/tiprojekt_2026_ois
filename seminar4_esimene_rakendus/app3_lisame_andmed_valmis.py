import streamlit as st
import pandas as pd
from openai import OpenAI

st.title("🎓 AI Kursuse Nõustaja - Samm 3")
st.caption("AI kasutab kursuste andmeid (esimesed 10 rida).")

# Külgriba API võtme jaoks
with st.sidebar:
    api_key = st.text_input("OpenRouter API Key", type="password")

# UUS
# Laeme andmed (andmed.csv peab olema samas kaustas või õigel teel)
# oluline on kasutada st.cache_data, et me ei laeks andmeid failist uuesti igal värskendamise korral
@st.cache_data(show_spinner="Andmete laadimine...")
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df.head(10) # Võtame esialgu vaid 10 rida testimiseks
df_sample = load_data("../andmed/puhtad_andmed.csv")


# VANA
# 1. Algatame vestluse ajaloo, kui seda veel pole
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Kuvame vestluse senise ajaloo (History)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Korjame üles uue kasutaja sisendi
if prompt := st.chat_input("Kirjelda, mida soovid õppida..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            error_msg = "Palun sisesta API võti!"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            
            # UUS Muudame loetud andmed tekstiks, mida AI-le saata
            courses_context = df_sample.to_string()
            sys_prompt="Oled Tartu ülikooli nõustaja. Kasuta järgmisi kursusi vastamiseks: \n"
            system_prompt = {
                "role": "system", 
                "content": sys_prompt + courses_context
            }
            
            messages_to_send = [system_prompt] + st.session_state.messages
            
            try:
                stream = client.chat.completions.create(
                    model="google/gemma-3-27b-it",
                    messages=messages_to_send,
                    stream=True
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Viga: {e}")
#TEST: tere anna mulle kõigi kursuste nimed, mida sa tead