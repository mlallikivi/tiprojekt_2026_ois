import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Pealkirjad
st.title("🎓 AI Kursuse Nõustaja - RAGiga")
st.caption("Täisväärtuslik RAG süsteem semantilise otsinguga.")

# Külgriba
with st.sidebar:
    api_key = st.text_input("OpenRouter API Key", type="password")

# UUS
# Mudelite ja andmete laadimine
# OLULINE: andmed on juba vektoriteks tehtud, loe need failist
# andmete embeddimise juhul kui faili pole teeme hiljem
# embed mudel, täisandmestik ja vektorandmebaas läheb cache'i
@st.cache_resource
def get_models():
    embedder = SentenceTransformer("BAAI/bge-m3")
    df = pd.read_csv("../andmed/puhtad_andmed.csv")
    embeddings_df = pd.read_pickle("../andmed/puhtad_andmed_embeddings.pkl")
    return embedder, df, embeddings_df
embedder, df, embeddings_df = get_models()

# 1. Algatame vestluse ajaloo, kui seda veel pole
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Kuvame vestluse senise ajaloo (History)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. KOrjame üles kasutaja sõnumi
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
            # 2. Semantiline otsing (RAG)
            with st.spinner("Otsin sobivaid kursusi..."):
                merged_df = pd.merge(df, embeddings_df, on='unique_ID')
                # Teeme kasutaja küsimusest vektori
                query_vec = embedder.encode([prompt])[0]
                
                # Arvutame koosinussarnasuse
                scores = cosine_similarity([query_vec], np.stack(merged_df['embedding']))[0]
                merged_df['score'] = scores
                
                # Leiame 5 kõige sarnasemat (suurim skoor)
                top5_df = merged_df.sort_values('score', ascending=False).head(5)
                top5_df.drop(['score', 'embedding'], axis=1, inplace=True)
                # Võtame andmetabelist vastavad read
                context_text = top5_df.to_string()

            # 3. LLM vastus koos kontekstiga
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            system_prompt = {
                "role": "system", 
                "content": f"Oled nõustaja. Kasuta järgmisi leitud kursusi vastamiseks:\n\n{context_text}"
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