from .base import BaseExtractor
from collections import defaultdict
import pdfplumber
import pandas as pd


class ScotiabankExtractor(BaseExtractor):
    COLUMN_RANGES = {
        "REF.#": (71, 103),
        "TRANS_DATE": (103, 132),
        "POST_DATE": (132, 162),
        "DETAILS": (162, 325),
        "AMOUNT": (325, 400),
    }

    def is_transaction_page(self, words):
        texts = {w["text"] for w in words}
        return "REF.#" in texts and "AMOUNT($)" in texts

    def is_header_row(self, row_words):
        texts = [w["text"] for w in row_words]
        return "REF.#" in texts or "DETAILS" in texts

    def is_subtotal_row(self, row_words):
        texts = " ".join(w["text"] for w in row_words)
        return "SUB-TOTAL" in texts

    def get_column(self, x0):
        for col, (start, end) in self.COLUMN_RANGES.items():
            if start <= x0 < end:
                return col
        return None

    def clean(self, df):
        # STEP 1: drop columns
        df = df.drop(columns=["POST_DATE", "PAGE"])

        # STEP 2: drop REF.#, replace with clean integer index
        df = df.drop(columns=["REF.#"])
        df.insert(0, "REF", range(1, len(df) + 1))

        # STEP 4: clean AMOUNT — convert "220.00-" → -220.00, rest → float
        def parse_amount(val):
            val = str(val).strip()
            if val.endswith("-"):
                return -float(val[:-1])
            return float(val)

        df["AMOUNT"] = df["AMOUNT"].apply(parse_amount)

        return df

    def extract(self, pdf_path):
        records = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                words = page.extract_words(x_tolerance=3, y_tolerance=3)

                if not self.is_transaction_page(words):
                    continue

                rows = defaultdict(lambda: defaultdict(str))
                words_by_top = defaultdict(list)

                for word in words:
                    top_key = round(word["top"], 0)
                    words_by_top[top_key].append(word)
                    col = self.get_column(word["x0"])
                    if col:
                        rows[top_key][col] = (
                            rows[top_key][col] + " " + word["text"]
                        ).strip()

                prev_ref = None
                for top_key in sorted(rows.keys()):
                    row = rows[top_key]
                    row_words = words_by_top[top_key]

                    if self.is_header_row(row_words) or self.is_subtotal_row(row_words):
                        continue

                    ref = row.get("REF.#", "").strip()

                    if ref and ref.isdigit():
                        prev_ref = ref
                        records.append(
                            {
                                "REF.#": ref,
                                "TRANS_DATE": row.get("TRANS_DATE", ""),
                                "POST_DATE": row.get("POST_DATE", ""),
                                "DETAILS": row.get("DETAILS", ""),
                                "AMOUNT": row.get("AMOUNT", ""),
                                "PAGE": page_num,
                            }
                        )
                    elif prev_ref and row.get("DETAILS"):
                        for r in reversed(records):
                            if r["REF.#"] == prev_ref:
                                r["DETAILS"] = (
                                    r["DETAILS"] + " " + row["DETAILS"]
                                ).strip()
                                break

        df = self.clean(pd.DataFrame(records))

        return df
