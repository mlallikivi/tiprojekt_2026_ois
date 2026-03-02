import pandas as pd
import streamlit as st

from app_logic.benchmark import load_benchmark_cases, load_last_benchmark_run, run_benchmark_suite, save_benchmark_run
from app_logic.config import BENCHMARK_CASES_PATH, BENCHMARK_RUNS_PATH


def initialize_benchmark_state():
    if "benchmark_results" not in st.session_state:
        st.session_state.benchmark_results = None
    if "benchmark_last_run_at" not in st.session_state:
        st.session_state.benchmark_last_run_at = None
    if "benchmark_case_count" not in st.session_state:
        st.session_state.benchmark_case_count = 0
    if "benchmark_source" not in st.session_state:
        st.session_state.benchmark_source = None


def get_benchmark_case_count():
    try:
        return len(load_benchmark_cases(BENCHMARK_CASES_PATH))
    except Exception:
        return 0


def render_benchmark_sidebar(api_key, benchmark_case_count):
    with st.sidebar:
        st.divider()
        st.subheader("Testikomplekt")
        st.caption(
            f"Kasutab faili `{BENCHMARK_CASES_PATH}`, ignoreerib aktiivseid filtreid, salvestab jooksutused faili `{BENCHMARK_RUNS_PATH}` ja kontrollib nii otsingut kui ka LLM-i."
        )
        benchmark_limit = st.slider(
            "Mitu testjuhtumit käivitada",
            min_value=0,
            max_value=benchmark_case_count,
            value=benchmark_case_count,
            step=1,
            help="Vali mitu esimest testjuhtumit failist jooksutada.",
        )
        run_clicked = st.button(
            "Käivita testikomplekt",
            disabled=not bool(api_key) or benchmark_case_count == 0,
            help=(
                None
                if api_key and benchmark_case_count > 0
                else "Sisesta OpenRouter API Key ja veendu, et benchmark fail sisaldab testjuhtumeid."
            ),
            use_container_width=True,
        )
        load_clicked = st.button(
            "Näita viimast salvestatud tulemust",
            use_container_width=True,
            help="Laeb viimasena faili salvestatud testikomplekti tulemuse.",
        )
        return run_clicked, load_clicked, benchmark_limit


def build_course_title_lookup(courses_df):
    title_lookup = {}

    for _, row in courses_df.iterrows():
        title = str(row.get("nimi_et", "")).strip()
        if not title:
            continue

        unique_id = str(row.get("unique_ID", "")).strip().upper()
        aine_kood = str(row.get("aine_kood", "")).strip().upper()

        if unique_id and unique_id not in title_lookup:
            title_lookup[unique_id] = title
        if aine_kood and aine_kood not in title_lookup:
            title_lookup[aine_kood] = title

    return title_lookup


def format_id_title_list(values, title_lookup):
    if not values:
        return "-"

    formatted_values = []
    for value in values:
        normalized_value = str(value).strip().upper()
        title = title_lookup.get(normalized_value, "Pealkiri puudub")
        formatted_values.append(f"{normalized_value} - {title}")

    return "\n".join(formatted_values)


def format_percentage(numerator, denominator):
    if denominator == 0:
        return "0.0%"

    return f"{(numerator / denominator) * 100:.1f}%"


def build_summary_dataframe(benchmark_results, title_lookup):
    rows = []
    for result in benchmark_results.case_results:
        rows.append(
            {
                "rea_nr": result.case.row_number,
                "paring": result.case.query,
                "oodatud_kursused": format_id_title_list(result.case.expected_ids, title_lookup),
                "vektorotsing_ok": "✅" if result.retrieval.passed else "❌",
                "lõpptulemus_ok": "✅" if result.llm.passed else "❌",
                "vektorotsingu_kursused": format_id_title_list(result.retrieval.returned_ids, title_lookup),
                "lõpptulemuse_kursused": format_id_title_list(result.llm.returned_ids, title_lookup),
                "vektorotsingus_puudu_kursused": format_id_title_list(result.retrieval.missing_ids, title_lookup),
                "lõpptulemuses_puudu_kursused": format_id_title_list(result.llm.missing_ids, title_lookup),
            }
        )
    return pd.DataFrame(rows)


def build_stage_dataframe(case_results, stage_name, title_lookup):
    rows = []
    for result in case_results:
        stage_result = getattr(result, stage_name)
        rows.append(
            {
                "rea_nr": result.case.row_number,
                "paring": result.case.query,
                "oodatud_kursused": format_id_title_list(result.case.expected_ids, title_lookup),
                "tagastatud_kursused": format_id_title_list(stage_result.returned_ids, title_lookup),
                "puuduolevad_kursused": format_id_title_list(stage_result.missing_ids, title_lookup),
            }
        )

    return pd.DataFrame(rows)


def build_vector_correct_llm_wrong_dataframe(case_results, title_lookup):
    rows = []
    for result in case_results:
        if not result.retrieval.passed or result.llm.passed:
            continue

        rows.append(
            {
                "rea_nr": result.case.row_number,
                "paring": result.case.query,
                "oodatud_kursused": format_id_title_list(result.case.expected_ids, title_lookup),
                "vektorotsingu_kursused": format_id_title_list(result.retrieval.returned_ids, title_lookup),
                "lõpptulemuse_kursused": format_id_title_list(result.llm.returned_ids, title_lookup),
                "lõpptulemuses_puudu_kursused": format_id_title_list(result.llm.missing_ids, title_lookup),
            }
        )

    return pd.DataFrame(rows)


def render_stage_results(case_results, stage_name, title_lookup):
    incorrect_results = [result for result in case_results if not getattr(result, stage_name).passed]
    correct_results = [result for result in case_results if getattr(result, stage_name).passed]

    with st.expander("Vigased", expanded=True):
        if incorrect_results:
            st.dataframe(build_stage_dataframe(incorrect_results, stage_name, title_lookup), hide_index=True)
        else:
            st.success("Vigaseid juhtumeid ei ole.")

    with st.expander("Korrektsed"):
        if correct_results:
            dataframe = build_stage_dataframe(correct_results, stage_name, title_lookup)
            st.dataframe(dataframe.drop(columns=["puuduolevad_kursused"], errors="ignore"), hide_index=True)
        else:
            st.info("Korrektselt läbitud juhtumeid ei ole.")


def render_benchmark_results(courses_df):
    benchmark_results = st.session_state.benchmark_results
    if not benchmark_results:
        return

    title_lookup = build_course_title_lookup(courses_df)

    st.subheader("Testikomplekti tulemused")
    if st.session_state.benchmark_last_run_at:
        source_label = f"Allikas: {st.session_state.benchmark_source}" if st.session_state.benchmark_source else ""
        caption_text = f"Viimane tulemus: {st.session_state.benchmark_last_run_at}"
        if source_label:
            caption_text = f"{caption_text}. {source_label}"
        st.caption(caption_text)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Vektorotsing õigeid", benchmark_results.retrieval_correct)
    metric_columns[1].metric("Vektorotsing valesid", benchmark_results.retrieval_incorrect)
    metric_columns[2].metric("Lõpptulemus õigeid", benchmark_results.llm_correct)
    metric_columns[3].metric("Lõpptulemus valesid", benchmark_results.llm_incorrect)

    percentage_columns = st.columns(2)
    percentage_columns[0].metric(
        "Vektorotsingu korrektsus",
        format_percentage(benchmark_results.retrieval_correct, benchmark_results.total_cases),
    )
    percentage_columns[1].metric(
        "Lõpptulemuse korrektsus",
        format_percentage(benchmark_results.llm_correct, benchmark_results.total_cases),
    )

    summary_tab, retrieval_tab, llm_tab, llm_only_fail_tab = st.tabs(
        ["Kokkuvõte", "Vektorotsing", "Lõpptulemus", "Vektorotsing õige, lõpptulemus vale"]
    )

    with summary_tab:
        st.dataframe(build_summary_dataframe(benchmark_results, title_lookup), hide_index=True)

    with retrieval_tab:
        render_stage_results(benchmark_results.case_results, "retrieval", title_lookup)

    with llm_tab:
        render_stage_results(benchmark_results.case_results, "llm", title_lookup)

    with llm_only_fail_tab:
        filtered_df = build_vector_correct_llm_wrong_dataframe(benchmark_results.case_results, title_lookup)
        if filtered_df.empty:
            st.success("Selliseid juhtumeid ei ole.")
        else:
            st.dataframe(filtered_df, hide_index=True)


def run_benchmark(api_key, embedder, courses_df, embeddings_df, benchmark_limit):
    progress_bar = st.progress(0, text="Valmistan testikomplekti ette...")
    progress_status = st.empty()

    def update_progress(completed, total, case):
        if total == 0:
            progress_bar.progress(100, text="Testikomplekt lõpetatud: 0 testjuhtumit.")
            progress_status.info("Testjuhtumeid ei valitud.")
            return

        percentage = int((completed / total) * 100)
        if completed == 0:
            progress_bar.progress(0, text=f"Valmistan ette {total} testjuhtumit...")
            progress_status.info(f"Alustan {total} testjuhtumi jooksutamist.")
            return

        current_query = case.query if case else ""
        progress_bar.progress(percentage, text=f"Jookseb testikomplekt: {completed}/{total}")
        progress_status.caption(f"Praegune juhtum {completed}/{total}: {current_query}")

    try:
        cases = load_benchmark_cases(BENCHMARK_CASES_PATH)
        st.session_state.benchmark_results = run_benchmark_suite(
            cases,
            embedder,
            courses_df,
            embeddings_df,
            api_key,
            case_limit=benchmark_limit,
            progress_callback=update_progress,
        )
        st.session_state.benchmark_last_run_at = save_benchmark_run(st.session_state.benchmark_results)
        st.session_state.benchmark_source = f"salvestatud faili `{BENCHMARK_RUNS_PATH}`"
        if benchmark_limit > 0:
            progress_bar.progress(100, text=f"Testikomplekt lõpetatud: {benchmark_limit} testjuhtumit.")
            progress_status.success("Testikomplekti jooksutamine valmis ja tulemus salvestati faili.")
    except FileNotFoundError:
        st.session_state.benchmark_results = None
        progress_bar.empty()
        progress_status.empty()
        st.error(f"Testikomplekti faili `{BENCHMARK_CASES_PATH}` ei leitud.")
    except Exception as error:
        st.session_state.benchmark_results = None
        progress_bar.empty()
        progress_status.empty()
        st.error(f"Testikomplekti jooksutamine ebaõnnestus: {error}")


def load_saved_benchmark():
    try:
        benchmark_results, saved_at = load_last_benchmark_run(BENCHMARK_RUNS_PATH)
        st.session_state.benchmark_results = benchmark_results
        st.session_state.benchmark_last_run_at = saved_at
        st.session_state.benchmark_source = f"laetud failist `{BENCHMARK_RUNS_PATH}`"
        st.success("Viimane salvestatud testikomplekti tulemus laetud.")
    except FileNotFoundError:
        st.error(f"Salvestatud tulemuste faili `{BENCHMARK_RUNS_PATH}` ei leitud.")
    except Exception as error:
        st.error(f"Salvestatud tulemuse laadimine ebaõnnestus: {error}")
