from pathlib import Path

try:
    from services.transactions import process_transactions
except ModuleNotFoundError:
    from src.services.transactions import process_transactions


def main():
    pdf_path = Path(__file__).resolve().parent.parent / "data" / "file.pdf"
    df = process_transactions(pdf_path)

    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
