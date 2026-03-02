import pandas as pd

from app_logic.config import HINDAMIS_MAP, LINN_MAP


def format_filters(filters):
    return (
        f"EAP:{filters['eap_range']}, "
        f"Sem:{filters['semester_opts']}, "
        f"Hind:{filters['hindamis_opts']}, "
        f"Linn:{filters['linn_opts']}, "
        f"Aste:{filters['aste_opts']}, "
        f"Veeb:{filters['veeb_opts']}, "
        f"Eeldusaineteta:{filters['no_prereqs']}"
    )


def get_location_mask(dataframe, selected_locations):
    location_mask = pd.Series(False, index=dataframe.index)

    for location in selected_locations:
        known_values = LINN_MAP.get(location, [])
        location_mask |= dataframe["linn"].isin(known_values)
        if location == "Tartu":
            location_mask |= dataframe["linn"].isna()

    return location_mask


def apply_filters(dataframe, filters):
    mask = pd.Series(True, index=dataframe.index)
    eap_min, eap_max = filters["eap_range"]

    mask &= dataframe["eap"].between(eap_min, eap_max)

    if filters["semester_opts"]:
        mask &= dataframe["semester"].isin(filters["semester_opts"])

    if filters["hindamis_opts"]:
        selected_grading = [HINDAMIS_MAP[item] for item in filters["hindamis_opts"]]
        mask &= dataframe["hindamisviis"].isin(selected_grading)

    if filters["linn_opts"]:
        mask &= get_location_mask(dataframe, filters["linn_opts"])

    if filters["aste_opts"]:
        pattern = "|".join(filters["aste_opts"])
        mask &= dataframe["oppeaste"].str.contains(pattern, case=False, na=False)

    if filters["veeb_opts"]:
        mask &= dataframe["veebiope"].isin(filters["veeb_opts"])

    if filters["no_prereqs"]:
        mask &= dataframe["eeldusained"].isna()

    return dataframe[mask].copy()

