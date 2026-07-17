import re

PROVINCES = r'\b(ON|BC|AB|QC|MB|SK|NS|NB|PE|NL|NT|YT|NU)\b'

def clean_desc(details: str) -> str:
    # 1. has # or 6+ digit sequence
    number_match = re.search(r'#\s*\d+|\d{6,}|\d+', details)
    if number_match:
        left = details[:number_match.start()].strip().rstrip('-*# ')
        if left:
            return left
        # number at start → take right, split at next digit block
        right = details[number_match.end():].strip()
        right_match = re.search(r'\d{4,}', right)
        if right_match:
            return right[:right_match.start()].strip()
        # split at province
        prov_match = re.search(PROVINCES, right)
        if prov_match:
            return right[:prov_match.start()].strip()
        return right

    # 3. no number → look for province
    prov_match = re.search(PROVINCES, details)
    if prov_match:
        left = details[:prov_match.start()].strip()
        words = left.split()
        if words:
            words = words[:-1]  # remove last word (city)
            # remove duplicate words (KINGSTON KINGSTON case)
            seen = []
            for w in words:
                if w not in seen:
                    seen.append(w)
            return ' '.join(seen).strip()

    # 4. keep as-is
    return details.strip()