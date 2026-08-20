from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.engines.dataset import DATASETS, MAX_FILE_SIZE_BYTES, load_dataset
from app.engines.execution import execute_rules
from app.engines.rules import interpret_custom_rule, suggest_rules
from app.models import DatasetProfile, Rule, RuleExecutionResult

app = FastAPI(title="Identity Data Analyzer API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class MappingRequest(BaseModel):
    field_mapping: dict[str, str]
class CustomRuleRequest(MappingRequest):
    text: str
class RunAnalysisRequest(BaseModel):
    rules: list[Rule]

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/datasets/upload", response_model=DatasetProfile)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetProfile:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 25 MB MVP limit")
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        _, profile = load_dataset(tmp_path, file.filename or "dataset")
        return profile
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if 'tmp_path' in locals(): tmp_path.unlink(missing_ok=True)

@app.post("/datasets/{dataset_id}/rules/suggest", response_model=list[Rule])
def rules_suggest(dataset_id: str, request: MappingRequest) -> list[Rule]:
    if dataset_id not in DATASETS: raise HTTPException(status_code=404, detail="Dataset not found")
    return suggest_rules(request.field_mapping)

@app.post("/datasets/{dataset_id}/rules/interpret", response_model=Rule)
def rules_interpret(dataset_id: str, request: CustomRuleRequest) -> Rule:
    if dataset_id not in DATASETS: raise HTTPException(status_code=404, detail="Dataset not found")
    return interpret_custom_rule(request.text, request.field_mapping)

@app.post("/datasets/{dataset_id}/analysis/run", response_model=list[RuleExecutionResult])
def run_analysis(dataset_id: str, request: RunAnalysisRequest) -> list[RuleExecutionResult]:
    df = DATASETS.get(dataset_id)
    if df is None: raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        return execute_rules(df, request.rules)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
