import csv
import os

from app_logic.config import FEEDBACK_LOG_PATH


def log_feedback(timestamp, prompt, filters, context_ids, context_names, response, rating, error_category):
    file_exists = os.path.isfile(FEEDBACK_LOG_PATH)

    with open(FEEDBACK_LOG_PATH, "a", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle)
        if not file_exists:
            writer.writerow(
                [
                    "Aeg",
                    "Kasutaja päring",
                    "Filtrid",
                    "Leitud ID-d",
                    "Leitud ained",
                    "LLM Vastus",
                    "Hinnang",
                    "Veatüüp",
                ]
            )
        writer.writerow(
            [
                timestamp,
                prompt,
                filters,
                str(context_ids),
                str(context_names),
                response,
                rating,
                error_category,
            ]
        )


def get_context_names(context_df):
    if context_df.empty:
        return []

    for column_name in ("aine_nimetus_est", "nimi_et"):
        if column_name in context_df.columns:
            return context_df[column_name].tolist()

    return []

