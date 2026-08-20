# Identity Data Analyzer MVP Architecture

Identity Data Analyzer separates multilingual IAM intent from deterministic data execution.

## Flow

1. Upload a CSV or XLSX dataset.
2. Profile columns, nulls, uniqueness, samples, and inferred IAM concepts.
3. Review or correct semantic field mappings.
4. Generate or enter natural-language rules.
5. Interpret rules into canonical, language-independent rule definitions.
6. Validate rules one at a time.
7. Execute only validated canonical rules through predefined operators.
8. Display KPIs, compliance rates, non-compliant records, distributions, duplicates, and insights.

## Backend Modules

- API: FastAPI routes for upload, mapping, rule suggestions, custom rule interpretation, validation, execution, and export.
- Dataset Analysis Engine: loads CSV/XLSX files and produces dataset profiles.
- IAM Semantic Mapping Engine: maps arbitrary column names to canonical IAM concepts with confidence scores.
- AI Rule Interpretation Engine: deterministic MVP heuristics that can be replaced by an LLM adapter without changing the rule engine.
- Canonical Rule Engine: Pydantic schemas and validation for rules and conditions.
- Rule Execution Engine: safe pandas execution using an allow-list of operators.
- Results Engine: per-rule summaries and overall compliance metrics.

## Frontend Structure

- DatasetPanel: upload state, profile, and editable concept mapping.
- AgentPanel: sequential rule suggestion, custom multilingual rule input, and interpreted logic.
- RulesPanel: validated/draft/rejected rules and Run Analysis.
- ResultsDashboard: overall score and rule-specific results.
