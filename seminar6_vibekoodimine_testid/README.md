# AI Kursuse Nõustaja

Streamlit application for recommending University of Tartu courses with a small retrieval-augmented generation pipeline and a built-in benchmark runner.

## What the project does

- Loads a cleaned course catalogue from `andmed/puhtad_andmed.csv`
- Loads precomputed sentence embeddings from `andmed/puhtad_andmed_embeddings.pkl`
- Lets the user filter courses in the sidebar
- Runs vector search over the filtered catalogue
- Sends the top retrieved courses to an LLM through OpenRouter
- Shows the answer together with debug information and feedback logging
- Evaluates benchmark cases from `benchmark_data/testjuhtumid.csv`

## Main features

### Course assistant

- Chat-style interface in Streamlit
- Sidebar filters for EAP, semester, grading, city, study level, study mode, and prerequisite-free courses
- Vector search using `SentenceTransformer` embeddings and cosine similarity
- Final answer generation with OpenRouter
- Debug view for retrieved courses and exact LLM prompt
- Feedback logging to `tagasiside_log.csv`

### Benchmark runner

- Runs benchmark cases from `benchmark_data/testjuhtumid.csv`
- Checks both:
  - vector search output
  - final LLM output
- Supports running only the first `0..N` test cases
- Shows progress while the benchmark is running
- Stores benchmark results in `benchmark_data/benchmark_runs.json`
- Can reload the most recently saved benchmark result
- Shows separate views for:
  - summary
  - vector search
  - final result
  - cases where vector search was correct but the final result was wrong

## Project structure

```text
.
├── app.py
├── README.md
├── environment.yml
├── andmed/
│   ├── puhtad_andmed.csv
│   └── puhtad_andmed_embeddings.pkl
├── benchmark_data/
│   ├── benchmark_runs.json
│   └── testjuhtumid.csv
├── app_logic/
│   ├── benchmark.py
│   ├── config.py
│   ├── data.py
│   ├── feedback.py
│   ├── filters.py
│   ├── llm.py
│   └── retrieval.py
└── app_ui/
    └── benchmark.py
```

## Module overview

### `app.py`

Thin Streamlit entrypoint. It now focuses on:

- app startup
- filter UI
- chat UI
- user prompt handling
- wiring the benchmark UI module into the page

### `app_logic/config.py`

Central constants and file paths, including:

- data files
- benchmark files
- model names
- filter mappings

### `app_logic/data.py`

Loads:

- course data
- embeddings
- sentence transformer model

### `app_logic/filters.py`

Applies all sidebar filters to the merged course dataframe.

### `app_logic/retrieval.py`

Handles:

- merging course data with embedding data
- vector similarity search
- top-k retrieval

### `app_logic/llm.py`

Handles:

- normal chat prompt building
- OpenRouter streaming responses
- benchmark-specific structured output parsing

### `app_logic/feedback.py`

Handles:

- feedback logging
- extracting course names for feedback logs

### `app_logic/benchmark.py`

Core benchmark logic:

- reading and normalizing `benchmark_data/testjuhtumid.csv`
- evaluating retrieval results
- evaluating LLM results
- serializing and loading saved benchmark runs

### `app_ui/benchmark.py`

Streamlit-specific benchmark UI:

- benchmark sidebar
- progress display
- results tables
- saved-result loading

This separation keeps the benchmark evaluation logic out of the main app entrypoint.

## Data files

### `andmed/puhtad_andmed.csv`

Main course catalogue. Important columns include:

- `unique_ID`
- `aine_kood`
- `nimi_et`
- `eap`
- `semester`
- `hindamisviis`
- `linn`
- `oppeaste`
- `veebiope`
- `kirjeldus`

### `andmed/puhtad_andmed_embeddings.pkl`

Pickled dataframe containing embeddings keyed by `unique_ID`.

### `benchmark_data/testjuhtumid.csv`

Benchmark file with:

- column 1: query text
- column 2: expected `unique_ID` values

Rules:

- multiple IDs may be separated by commas or semicolons
- `-` means the expected result is empty

## Benchmark scoring

The benchmark uses two stages:

1. `Vektorotsing`
2. `Lõpptulemus`

Pass rule:

- A case is correct if all expected IDs are included in the returned IDs.
- Extra returned IDs do not fail the case.
- For `-` rows, the stage is correct only if it returns no IDs.

## Saved benchmark runs

Benchmark runs are appended to:

- `benchmark_data/benchmark_runs.json`

Each saved run includes:

- save timestamp
- aggregate metrics
- per-case results for retrieval and final result

## Setup

The repository includes a Conda environment definition:

```bash
conda env create -f environment.yml
conda activate oisi_projekt
```

## Running the app

```bash
streamlit run app.py
```

## Configuration notes

- The embedding model is `BAAI/bge-m3`
- The final answer model is configured in `app_logic/config.py`
- The app expects an OpenRouter API key in the sidebar

## Limitations

- Initial model loading may require internet access if the embedding model is not cached locally
- Benchmark quality depends on the benchmark file and the top-k retrieval behaviour
- The final result stage is only as good as the LLM output and the constrained benchmark prompt

## Typical workflow

1. Start the Streamlit app.
2. Enter the OpenRouter API key.
3. Ask for course recommendations with or without filters.
4. Inspect retrieval debug data if needed.
5. Run the benchmark from the sidebar.
6. Review vector-search vs final-result correctness.
7. Reload the latest saved benchmark result later if needed.
