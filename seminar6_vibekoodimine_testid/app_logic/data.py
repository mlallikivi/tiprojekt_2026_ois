import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer

from app_logic.config import COURSE_DATA_PATH, EMBEDDINGS_PATH, EMBEDDER_NAME


@st.cache_resource
def get_models():
    embedder = SentenceTransformer(EMBEDDER_NAME)
    courses_df = pd.read_csv(COURSE_DATA_PATH)
    embeddings_df = pd.read_pickle(EMBEDDINGS_PATH)
    return embedder, courses_df, embeddings_df

