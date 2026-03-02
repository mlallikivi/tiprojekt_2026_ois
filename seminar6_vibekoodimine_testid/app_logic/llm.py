import json
import re

from openai import OpenAI

from app_logic.config import MODEL_NAME, OPENROUTER_BASE_URL


def build_system_prompt(context_text):
    return {
        "role": "system",
        "content": (
            "Oled nõustaja. Järgi kasutaja palveid ning kasuta vastamiseks ainult järgmisi kursusi:\n\n"
            f"{context_text}"
        ),
    }


def build_messages_to_send(system_prompt, session_messages):
    history = [
        {"role": message["role"], "content": message["content"]}
        for message in session_messages
        if "debug_info" not in message
    ]
    return [system_prompt] + history


def create_response_stream(api_key, messages_to_send):
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    return client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages_to_send,
        stream=True,
    )


def build_benchmark_system_prompt(context_text):
    return {
        "role": "system",
        "content": (
            "Oled kursuste hindamise abiline. Kasuta ainult antud kursuste konteksti. "
            "Kasuta ainult välja `unique_ID` väärtusi. "
            "Ära kasuta rea numbreid, tabeli indekseid ega muid koode. "
            "Tagasta ainult lubatud `unique_ID` väärtused, mis on kontekstis selgelt ette antud. "
            "Vasta ainult kehtiva JSON-objektina kujul "
            '{"course_ids": ["ID1", "ID2"]}. '
            'Kui ükski kursus ei sobi, vasta kujul {"course_ids": []}. '
            "Ära lisa selgitusi, markdowni ega muud teksti."
            f"\n\nKursuste kontekst:\n{context_text}"
        ),
    }


def build_benchmark_user_prompt(query):
    return {
        "role": "user",
        "content": (
            "Kasuta ainult antud kursuste konteksti ning tagasta sobivate kursuste unique_ID väärtused päringu jaoks: "
            f"{query}"
        ),
    }


def _extract_message_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)

    return ""


def create_benchmark_completion(api_key, messages):
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False,
    )
    content = response.choices[0].message.content if response.choices else ""
    return _extract_message_text(content).strip()


def _extract_json_payload(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_benchmark_id(value):
    normalized_value = str(value).strip().upper()
    return normalized_value.replace(" ", "")


def _extract_id_list_from_payload(payload):
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        raise ValueError("Benchmark response is not a JSON object.")

    for key in ("course_ids", "unique_ids", "ids", "courses", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value

    raise ValueError("Benchmark response does not contain a supported ID list field.")


def _extract_id_value(item):
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        for key in ("unique_ID", "unique_id", "course_id", "id"):
            value = item.get(key)
            if isinstance(value, str):
                return value

    return None


def _extract_ids_from_text(response_text):
    pattern = r"[A-Z0-9]+\.[A-Z0-9]+\.[A-Z0-9_]+"
    return re.findall(pattern, response_text.upper())


def parse_benchmark_ids(response_text):
    normalized_ids = []
    seen = set()

    try:
        payload = _extract_json_payload(response_text)
        course_ids = _extract_id_list_from_payload(payload)
        raw_values = [_extract_id_value(course_id) for course_id in course_ids]
    except Exception:
        raw_values = _extract_ids_from_text(response_text)

    for course_id in raw_values:
        if course_id is None:
            continue

        normalized_id = _normalize_benchmark_id(course_id)

        if normalized_id and normalized_id not in seen:
            seen.add(normalized_id)
            normalized_ids.append(normalized_id)

    return normalized_ids
