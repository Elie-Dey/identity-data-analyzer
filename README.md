# Identity Data Analyzer

AI-assisted IAM and identity data analysis MVP. The application lets a user upload CSV/XLSX identity data, profile the dataset, review IAM semantic mappings, validate rules one by one, and execute only canonical structured rules through a deterministic engine.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the modular architecture, data flow, canonical rule model, semantic mapping strategy, API surface, and frontend component structure.

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API endpoints:

- `POST /datasets/upload` — upload CSV/XLSX and return a dataset profile.
- `POST /datasets/{dataset_id}/rules/suggest` — propose sequential IAM rules from reviewed mapping.
- `POST /datasets/{dataset_id}/rules/interpret` — convert multilingual custom rule text into canonical logic.
- `POST /datasets/{dataset_id}/analysis/run` — execute validated rules safely.

## Frontend

```bash
npm install
npm run dev
```

Set `VITE_API_URL` if the API is not running on `http://localhost:8000`.

## Testing

```bash
python -m pytest tests
npm run build
```

Sample data and natural-language IAM rules are available in `samples/`.
