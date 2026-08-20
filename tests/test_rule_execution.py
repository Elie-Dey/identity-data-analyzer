import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.engines.dataset import profile_dataframe
from app.engines.execution import execute_rule
from app.engines.rules import suggest_rules, interpret_custom_rule
import pandas as pd


def test_profile_mapping_and_employee_id_rule():
    df = pd.read_csv("samples/identity_users.csv")
    profile = profile_dataframe("test", "identity_users.csv", df)
    assert profile.field_mapping["employeeID"].value == "EMPLOYEE_ID"
    rules = suggest_rules({k: v.value for k, v in profile.field_mapping.items()})
    rule = next(r for r in rules if "Employee ID" in r.name)
    rule.status = "validated"
    result = execute_rule(df, rule)
    assert result.non_compliant_count == 1
    assert result.compliance_rate == 80.0


def test_multilingual_custom_service_rule():
    mapping = {"username": "USERNAME", "accountType": "ACCOUNT_TYPE"}
    rule = interpret_custom_rule("Vérifie que les comptes dont le username commence par svc_ sont identifiés comme Service Accounts.", mapping)
    assert rule.source_language == "fr"
    assert rule.canonical_logic.scope[0].operator.value == "starts_with"
    assert rule.canonical_logic.assertions[0].value == "Service"
