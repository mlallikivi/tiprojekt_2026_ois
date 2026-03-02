from datetime import datetime

import pandas as pd
import streamlit as st

from app_logic.config import DISPLAY_COLUMNS, HINDAMIS_MAP, LINN_MAP
from app_logic.data import get_models
from app_logic.feedback import get_context_names, log_feedback
from app_logic.filters import apply_filters, format_filters
from app_logic.llm import build_messages_to_send, build_system_prompt, create_response_stream
from app_logic.retrieval import merge_course_data, rank_courses
from app_ui.benchmark import (
    get_benchmark_case_count,
    initialize_benchmark_state,
    load_saved_benchmark,
    render_benchmark_results,
    render_benchmark_sidebar,
    run_benchmark,
)


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    initialize_benchmark_state()


def render_sidebar_filters(courses_df):
    with st.sidebar:
        st.header("⚙️ Seaded ja filtrid")
        api_key = st.text_input("OpenRouter API Key", type="password")
        st.divider()

        st.subheader("Filtreeri kursusi")
        max_eap = float(courses_df["eap"].max()) if "eap" in courses_df.columns else 60.0
        filters = {
            "eap_range": st.slider("EAP maht", 0.0, max_eap, (0.0, max_eap), step=1.0),
            "semester_opts": st.multiselect("Semester", ["kevad", "sügis"]),
            "hindamis_opts": st.multiselect("Hindamisviis", list(HINDAMIS_MAP)),
            "linn_opts": st.multiselect("Linn", list(LINN_MAP)),
            "aste_opts": st.multiselect("Õppeaste", ["bakalaureuse", "magistri", "doktori"]),
            "veeb_opts": st.multiselect("Õppevorm", ["põimõpe", "lähiõpe", "veebiõpe"]),
            "no_prereqs": st.checkbox("Ainult ilma eeldusaineteta kursused"),
        }

    return api_key, filters


def render_debug_info(debug_info, message_index):
    with st.expander("🔍 Vaata kapoti alla (RAG ja filtrid)"):
        st.caption(f"**Aktiivsed filtrid:** {debug_info.get('filters', 'Info puudub')}")
        st.write(f"Filtrid jätsid andmestikku alles **{debug_info.get('filtered_count', 0)}** kursust.")

        st.write("**RAG otsingu tulemus (Top 5 leitud kursust):**")
        context_df = debug_info.get("context_df", pd.DataFrame())
        if not context_df.empty:
            columns_to_show = [column for column in DISPLAY_COLUMNS if column in context_df.columns]
            st.dataframe(context_df[columns_to_show], hide_index=True)
        else:
            st.warning("Ühtegi kursust ei leitud (kas filtrid olid liiga karmid või andmestik tühi).")

        st.text_area(
            "LLM-ile saadetud täpne prompt:",
            debug_info.get("system_prompt", ""),
            height=150,
            disabled=True,
            key=f"prompt_area_{message_index}",
        )


def render_feedback_form(debug_info, assistant_message, message_index):
    with st.expander("📝 Hinda vastust (Salvestab logisse)"):
        with st.form(key=f"feedback_form_{message_index}"):
            rating = st.radio(
                "Hinnang vastusele:",
                ["👍 Hea", "👎 Halb"],
                horizontal=True,
                key=f"rating_{message_index}",
            )
            error_category = st.selectbox(
                "Kui vastus oli halb, siis mis läks valesti?",
                [
                    "",
                    "Filtrid olid liiga karmid/valed",
                    "Otsing leidis valed ained (RAG viga)",
                    "LLM hallutsineeris/vastas valesti",
                ],
                key=f"kato_{message_index}",
            )
            if st.form_submit_button("Salvesta hinnang"):
                context_df = debug_info.get("context_df", pd.DataFrame())
                log_feedback(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    prompt=debug_info.get("user_prompt", ""),
                    filters=debug_info.get("filters", ""),
                    context_ids=context_df["unique_ID"].tolist() if not context_df.empty else [],
                    context_names=get_context_names(context_df),
                    response=assistant_message["content"],
                    rating=rating,
                    error_category=error_category,
                )
                st.success("Tagasiside salvestatud tagasiside_log.csv faili!")


def render_chat_history():
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and "debug_info" in message:
                debug_info = message["debug_info"]
                render_debug_info(debug_info, index)
                render_feedback_form(debug_info, message, index)


def handle_user_prompt(prompt, api_key, filters, embedder, courses_df, embeddings_df):
    current_filters_str = format_filters(filters)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            error_message = "Palun sisesta API võti!"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            return

        with st.spinner("Otsin sobivaid kursusi..."):
            merged_df = merge_course_data(courses_df, embeddings_df)
            filtered_df = apply_filters(merged_df, filters)
            ranked_df, context_text = rank_courses(embedder, filtered_df, prompt)
            results_df_display = ranked_df.drop(columns=["embedding"], errors="ignore").copy()
            system_prompt = build_system_prompt(context_text)
            messages_to_send = build_messages_to_send(system_prompt, st.session_state.messages)

            try:
                response = st.write_stream(create_response_stream(api_key, messages_to_send))
            except Exception as error:
                st.error(f"Viga: {error}")
                return

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "debug_info": {
                        "user_prompt": prompt,
                        "filters": current_filters_str,
                        "filtered_count": len(filtered_df),
                        "context_df": results_df_display,
                        "system_prompt": system_prompt["content"],
                    },
                }
            )
            st.rerun()


def main():
    embedder, courses_df, embeddings_df = get_models()

    st.title("🎓 AI Kursuse Nõustaja - Samm 6")
    st.caption("RAG süsteem koos kapotialuse analüüsi ja tagasiside logimisega.")

    initialize_session_state()
    st.session_state.benchmark_case_count = get_benchmark_case_count()
    api_key, filters = render_sidebar_filters(courses_df)
    run_benchmark_clicked, load_benchmark_clicked, benchmark_limit = render_benchmark_sidebar(
        api_key, st.session_state.benchmark_case_count
    )

    if run_benchmark_clicked:
        run_benchmark(api_key, embedder, courses_df, embeddings_df, benchmark_limit)
    if load_benchmark_clicked:
        load_saved_benchmark()

    render_benchmark_results(courses_df)
    render_chat_history()

    prompt = st.chat_input("Kirjelda, mida soovid õppida...")
    if prompt:
        handle_user_prompt(prompt, api_key, filters, embedder, courses_df, embeddings_df)


if __name__ == "__main__":
    main()
