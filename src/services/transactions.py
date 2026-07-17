from src.extractors.scotiabank import ScotiabankExtractor
from src.utils.categorize_desc import get_category
from src.utils.format_desc import clean_desc


def process_transactions(pdf_path):
    extractor = ScotiabankExtractor()
    df = extractor.extract(pdf_path)
    df["DETAILS"] = df["DETAILS"].apply(clean_desc)
    df["category"] = df["DETAILS"].apply(get_category)
    return df


def transactions_to_records(df):
    return df.to_dict(orient="records")
