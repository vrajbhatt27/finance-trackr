"""
run_locally.py

Starts the FastAPI application locally using Uvicorn.

Usage:
    python run_locally.py
"""

import uvicorn


def main() -> None:
    uvicorn.run(
        "src.main:app",  # <module>:<FastAPI instance>
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info",
    )


if __name__ == "__main__":
    main()
