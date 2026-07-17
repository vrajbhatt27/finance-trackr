import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

try:
    from services.transactions import process_transactions, transactions_to_records
except ModuleNotFoundError:
    from src.services.transactions import process_transactions, transactions_to_records


app = FastAPI(title="Finance Trackr API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transactions/upload")
async def upload_transactions(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(await file.read())

    try:
        df = process_transactions(temp_path)
        return {
            "count": len(df),
            "transactions": transactions_to_records(df),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)
