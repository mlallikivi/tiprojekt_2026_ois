import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from app_logic.config import DEFAULT_EMPTY_CONTEXT


def merge_course_data(courses_df, embeddings_df):
    return pd.merge(courses_df, embeddings_df, on="unique_ID")


def get_top_courses(embedder, merged_df, prompt, top_k=5):
    if merged_df.empty:
        return pd.DataFrame()

    query_vec = embedder.encode([prompt])[0]
    ranked_df = merged_df.copy()
    ranked_df["score"] = cosine_similarity([query_vec], np.stack(ranked_df["embedding"]))[0]
    return ranked_df.sort_values("score", ascending=False).head(top_k)


def rank_courses(embedder, filtered_df, prompt):
    top_results = get_top_courses(embedder, filtered_df, prompt, top_k=5)
    if top_results.empty:
        return pd.DataFrame(), DEFAULT_EMPTY_CONTEXT

    context_text = top_results.drop(columns=["score", "embedding"], errors="ignore").to_string()
    return top_results, context_text
