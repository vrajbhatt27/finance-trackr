import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.services.transactions import process_transactions, transactions_to_records


router = APIRouter()
SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/transactions/upload")
async def upload_transactions(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and image files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
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
