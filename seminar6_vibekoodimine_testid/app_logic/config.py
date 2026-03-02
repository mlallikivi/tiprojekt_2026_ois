FEEDBACK_LOG_PATH = "tagasiside_log.csv"
COURSE_DATA_PATH = "andmed/puhtad_andmed.csv"
EMBEDDINGS_PATH = "andmed/puhtad_andmed_embeddings.pkl"
BENCHMARK_CASES_PATH = "benchmark_data/testjuhtumid.csv"
BENCHMARK_RUNS_PATH = "benchmark_data/benchmark_runs.json"
EMBEDDER_NAME = "BAAI/bge-m3"
MODEL_NAME = "google/gemma-3-27b-it"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_EMPTY_CONTEXT = "Sobivaid kursusi ei leitud."
DISPLAY_COLUMNS = ["unique_ID", "nimi_et", "eap", "semester", "oppeaste", "score"]
HINDAMIS_MAP = {
    "Eristav": "Eristav (A, B, C, D, E, F, mi)",
    "Eristamata": "Eristamata (arv, m.arv, mi)",
}
LINN_MAP = {
    "Tartu": ["Tartu linn", "Tartu"],
    "Tallinn": ["Tallinn"],
    "Narva": ["Narva linn"],
    "Pärnu": ["Pärnu linn"],
    "Viljandi": ["Viljandi linn"],
    "Tõravere": ["Tõravere alevik"],
}
