from __future__ import annotations

from typing import Annotated

try:
    from dotenv import load_dotenv

    load_dotenv(".env")
    load_dotenv(".env.local", override=True)
    load_dotenv(".local.env", override=True)
except Exception:
    pass

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from backend.agents.orchestrator import analyze_fixture, analyze_text
from backend.parsing.paper_parser import extract_pdf_text, list_fixtures, load_fixture_text
from backend.storage.evidence_board import run_store


app = FastAPI(
    title="RefereeOS API",
    description="AG2 + Daytona multi-agent preprint triage and reproducibility assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "RefereeOS"}


@app.get("/api/fixtures")
def fixtures() -> dict:
    return {"fixtures": list_fixtures()}


@app.post("/api/analyze")
async def analyze(
    fixture_id: Annotated[str, Form()] = "clean",
    field_domain: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> dict:
    if file and file.filename:
        if file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            text = extract_pdf_text(file.file)
        else:
            text = (await file.read()).decode("utf-8", errors="ignore")
        _, fixture_meta = load_fixture_text("clean")
        fixture_meta["fixture_id"] = "uploaded"
        board = analyze_text(text, source=f"uploaded_file:{file.filename}", fixture_meta=fixture_meta, field_domain=field_domain)
    else:
        board = analyze_fixture(fixture_id=fixture_id, field_domain=field_domain)

    run = run_store.create(board)
    return run


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict:
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/api/runs/{run_id}/evidence-board")
def get_evidence_board(run_id: str) -> dict:
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run["board"]


@app.get("/api/runs/{run_id}/packet", response_class=PlainTextResponse)
def get_packet(run_id: str) -> str:
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run["packet"]
