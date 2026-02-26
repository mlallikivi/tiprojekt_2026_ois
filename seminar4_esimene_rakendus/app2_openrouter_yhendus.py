import streamlit as st
from openai import OpenAI

# Iluasjad: pealkiri, allkiri
st.title("🎓 AI Kursuse Nõustaja - Samm 2")
st.caption("Vestlus päris tehisintellektiga (Gemma 3).")

# UUS 
# Külgriba API võtme jaoks (sidebar)


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
    #kuvame kohe kasutaja sõnumi
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # defineerime süsteemiprompti, 
    # genereerime vastuse, kontrollime ka, et kas võti on olemas (külgriba väljund)
    # kuvame vastuse striimina, ilmub jooksvalt
    with st.chat_message("assistant"):
        if not api_key:
            pass #todo: define error msg, display, save to history, like app1
        else:
            #defineeri OpenAI klient, anna sellele süsteemiprompt ja vestluse ajalugu
            #todo
                        
            try:
                # Kasutame OpenAI kliendi võimalust striimimida, et vastus ilmuks jooksvalt
                stream = None #Todo
                
                response = st.write_stream(stream) 
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Viga: {e}")