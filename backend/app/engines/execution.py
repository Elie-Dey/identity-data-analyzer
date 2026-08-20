from __future__ import annotations

import pandas as pd
from app.models import Operator, Rule, RuleExecutionResult


def _mask(df: pd.DataFrame, field: str, operator: Operator, value=None) -> pd.Series:
    if field not in df.columns:
        raise ValueError(f"Missing required field: {field}")
    s = df[field]
    text = s.fillna("").astype(str)
    if operator == Operator.equals: return text.str.lower() == str(value).lower()
    if operator == Operator.not_equals: return text.str.lower() != str(value).lower()
    if operator == Operator.is_empty: return s.isna() | (text.str.strip() == "")
    if operator == Operator.is_not_empty: return ~(s.isna() | (text.str.strip() == ""))
    if operator == Operator.starts_with: return text.str.startswith(str(value), na=False)
    if operator == Operator.ends_with: return text.str.endswith(str(value), na=False)
    if operator == Operator.contains: return text.str.contains(str(value), case=False, regex=False, na=False)
    if operator == Operator.not_contains: return ~text.str.contains(str(value), case=False, regex=False, na=False)
    if operator == Operator.greater_than: return pd.to_numeric(s, errors="coerce") > float(value)
    if operator == Operator.less_than: return pd.to_numeric(s, errors="coerce") < float(value)
    if operator == Operator.in_: return text.str.lower().isin([str(v).lower() for v in value])
    if operator == Operator.not_in: return ~text.str.lower().isin([str(v).lower() for v in value])
    if operator == Operator.matches_regex: return text.str.contains(str(value), regex=True, na=False)
    if operator == Operator.is_duplicate: return s.notna() & text.ne("") & s.duplicated(keep=False)
    if operator == Operator.exists: return pd.Series([field in df.columns] * len(df), index=df.index)
    if operator == Operator.does_not_exist: return pd.Series([field not in df.columns] * len(df), index=df.index)
    raise ValueError(f"Unsupported operator: {operator}")


def execute_rule(df: pd.DataFrame, rule: Rule) -> RuleExecutionResult:
    if rule.result_type == "distribution" and rule.canonical_logic.group_by:
        counts = df[rule.canonical_logic.group_by].fillna("<empty>").astype(str).value_counts().to_dict()
        return RuleExecutionResult(rule_id=rule.id, rule_name=rule.name, result_type=rule.result_type, total_scoped_records=len(df), distribution={str(k): int(v) for k, v in counts.items()}, insight=f"Distribution generated for {rule.canonical_logic.group_by}.")
    scoped = pd.Series([True] * len(df), index=df.index)
    for cond in rule.canonical_logic.scope:
        scoped &= _mask(df, cond.field, cond.operator, cond.value)
    scoped_df = df[scoped]
    if not rule.canonical_logic.assertions:
        return RuleExecutionResult(rule_id=rule.id, rule_name=rule.name, result_type=rule.result_type, total_scoped_records=len(scoped_df), count=len(scoped_df), insight="Rule counted scoped records.")
    compliant = pd.Series([True] * len(scoped_df), index=scoped_df.index)
    for assertion in rule.canonical_logic.assertions:
        assertion_mask = _mask(scoped_df, assertion.field, assertion.operator, assertion.value)
        compliant = assertion_mask if assertion.operator == Operator.is_duplicate else compliant & assertion_mask
    if rule.result_type == "duplicates":
        records = scoped_df[compliant].head(500).fillna("").to_dict(orient="records")
        return RuleExecutionResult(rule_id=rule.id, rule_name=rule.name, result_type=rule.result_type, total_scoped_records=len(scoped_df), count=int(compliant.sum()), records=records, insight=f"Detected {int(compliant.sum())} duplicate records.")
    non_compliant = ~compliant
    total = len(scoped_df)
    good = int(compliant.sum())
    bad = int(non_compliant.sum())
    rate = round((good / total) * 100, 2) if total else 100.0
    records = scoped_df[non_compliant].head(500).fillna("").to_dict(orient="records")
    return RuleExecutionResult(rule_id=rule.id, rule_name=rule.name, result_type=rule.result_type, total_scoped_records=total, compliant_count=good, non_compliant_count=bad, compliance_rate=rate, records=records, insight=f"{bad} non-compliant records found; compliance rate is {rate}%.")


def execute_rules(df: pd.DataFrame, rules: list[Rule]) -> list[RuleExecutionResult]:
    return [execute_rule(df, rule) for rule in rules if rule.enabled and rule.status == "validated"]
