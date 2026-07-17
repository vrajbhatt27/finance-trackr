import json
import re
from pathlib import Path


MAP_PATH = Path(__file__).resolve().parent.parent / "data" / "desc_category_map.json"


def load_desc_category_map():
    with MAP_PATH.open() as file:
        return json.load(file)


def iter_category_keywords(desc_map):
    for category, keywords in desc_map.items():
        yield category, category
        for keyword in keywords:
            yield category, keyword


def keyword_to_pattern(keyword):
    parts = re.split(r"\s+", str(keyword).strip())
    return r"[\W_]+".join(re.escape(part) for part in parts if part)


def get_category(details, desc_map=None, default="Uncategorized"):
    desc_map = desc_map or load_desc_category_map()
    detail = str(details)

    for category, keyword in iter_category_keywords(desc_map):
        pattern = keyword_to_pattern(keyword)
        if pattern and re.search(pattern, detail, re.IGNORECASE):
            return category

    return default
