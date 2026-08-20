from __future__ import annotations

import uuid
from pathlib import Path
import pandas as pd
from app.engines.semantic_mapping import build_mapping, infer_concept
from app.models import ColumnProfile, DatasetProfile

DATASETS: dict[str, pd.DataFrame] = {}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024


def load_dataset(path: Path, filename: str) -> tuple[str, DatasetProfile]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError("Only CSV and XLSX files are supported")
    dataset_id = str(uuid.uuid4())
    DATASETS[dataset_id] = df
    return dataset_id, profile_dataframe(dataset_id, filename, df)


def profile_dataframe(dataset_id: str, filename: str, df: pd.DataFrame) -> DatasetProfile:
    columns: list[ColumnProfile] = []
    for name in df.columns:
        series = df[name]
        empty = int(series.isna().sum() + (series.astype(str).str.strip() == "").sum())
        concept, confidence = infer_concept(str(name))
        samples = [v for v in series.dropna().astype(str).head(5).tolist()]
        columns.append(ColumnProfile(
            name=str(name), data_type=str(series.dtype), empty_count=empty,
            empty_percentage=round((empty / max(len(df), 1)) * 100, 2),
            unique_count=int(series.nunique(dropna=True)), sample_values=samples,
            semantic_meaning=concept, semantic_confidence=confidence,
        ))
    return DatasetProfile(
        dataset_id=dataset_id, filename=filename, total_records=len(df),
        total_columns=len(df.columns), columns=columns,
        field_mapping=build_mapping([str(c) for c in df.columns]),
    )
