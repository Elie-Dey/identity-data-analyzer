from __future__ import annotations

from app.models import CanonicalLogic, IdentityConcept, Operator, Rule, RuleCategory, RuleCondition


def detect_language(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["vérifie", "comptes", "possèdent", "n'ont"]):
        return "fr"
    if any(word in lowered for word in ["verifica", "cuentas", "tengan"]):
        return "es"
    return "en"


def suggest_rules(mapping: dict[str, str]) -> list[Rule]:
    by_concept = {v: k for k, v in mapping.items()}
    rules: list[Rule] = []
    def add(rule: Rule):
        rule.id = f"R{len(rules)+1:03d}"; rules.append(rule)
    if "ACCOUNT_TYPE" in by_concept and "EMPLOYEE_ID" in by_concept:
        add(Rule(id="", name="Human accounts require Employee ID", description="Find human accounts missing an employee identifier.", category=RuleCategory.identity_data_quality, canonical_logic=CanonicalLogic(scope=[RuleCondition(field=by_concept["ACCOUNT_TYPE"], operator=Operator.equals, value="Human", concept=IdentityConcept.ACCOUNT_TYPE)], assertions=[RuleCondition(field=by_concept["EMPLOYEE_ID"], operator=Operator.is_not_empty, concept=IdentityConcept.EMPLOYEE_ID)]), dataset_field_mapping={"ACCOUNT_TYPE": by_concept["ACCOUNT_TYPE"], "EMPLOYEE_ID": by_concept["EMPLOYEE_ID"]}, result_type="compliance_rate", severity="high"))
    if "ACCOUNT_STATUS" in by_concept and "MANAGER" in by_concept:
        add(Rule(id="", name="Active accounts require Manager", description="Identify active identities without a manager.", category=RuleCategory.account_governance, canonical_logic=CanonicalLogic(scope=[RuleCondition(field=by_concept["ACCOUNT_STATUS"], operator=Operator.in_, value=["Active", "Enabled", "True"], concept=IdentityConcept.ACCOUNT_STATUS)], assertions=[RuleCondition(field=by_concept["MANAGER"], operator=Operator.is_not_empty, concept=IdentityConcept.MANAGER)]), dataset_field_mapping={"ACCOUNT_STATUS": by_concept["ACCOUNT_STATUS"], "MANAGER": by_concept["MANAGER"]}, result_type="compliance_rate", severity="medium"))
    if "EMAIL" in by_concept:
        add(Rule(id="", name="Duplicate email detection", description="Detect duplicate email addresses across identities.", category=RuleCategory.duplicate_detection, canonical_logic=CanonicalLogic(assertions=[RuleCondition(field=by_concept["EMAIL"], operator=Operator.is_duplicate, concept=IdentityConcept.EMAIL)]), dataset_field_mapping={"EMAIL": by_concept["EMAIL"]}, result_type="duplicates", severity="medium"))
    if "ACCOUNT_TYPE" in by_concept:
        add(Rule(id="", name="Account distribution by type", description="Show the account population by account type.", category=RuleCategory.account_governance, canonical_logic=CanonicalLogic(group_by=by_concept["ACCOUNT_TYPE"]), dataset_field_mapping={"ACCOUNT_TYPE": by_concept["ACCOUNT_TYPE"]}, result_type="distribution", severity="low"))
    return rules


def interpret_custom_rule(text: str, mapping: dict[str, str]) -> Rule:
    language = detect_language(text)
    by_concept = {v: k for k, v in mapping.items()}
    lowered = text.lower()
    if "duplicate" in lowered or "duplic" in lowered or "doubl" in lowered:
        field = by_concept.get("EMAIL") or by_concept.get("EMPLOYEE_ID") or next(iter(mapping), "")
        name = f"Duplicate {field} detection"
        assertion = RuleCondition(field=field, operator=Operator.is_duplicate)
        result_type = "duplicates"
    elif "svc_" in lowered or "service" in lowered:
        user_field = by_concept.get("USERNAME", "username")
        type_field = by_concept.get("ACCOUNT_TYPE", "accountType")
        return Rule(id="CUSTOM", name="Service account classification", description="Service-style usernames must be classified as service accounts.", category=RuleCategory.account_governance, source_language=language, original_input=text, canonical_logic=CanonicalLogic(scope=[RuleCondition(field=user_field, operator=Operator.starts_with, value="svc_", concept=IdentityConcept.USERNAME)], assertions=[RuleCondition(field=type_field, operator=Operator.equals, value="Service", concept=IdentityConcept.ACCOUNT_TYPE)]), dataset_field_mapping={"USERNAME": user_field, "ACCOUNT_TYPE": type_field}, result_type="compliance_rate", severity="medium")
    else:
        field = by_concept.get("MANAGER") or by_concept.get("EMPLOYEE_ID") or next(iter(mapping), "")
        name = f"{field} must be populated"
        assertion = RuleCondition(field=field, operator=Operator.is_not_empty)
        result_type = "compliance_rate"
    return Rule(id="CUSTOM", name=name, description="Interpreted from a natural-language custom rule.", category=RuleCategory.custom_business_rule, source_language=language, original_input=text, canonical_logic=CanonicalLogic(assertions=[assertion]), dataset_field_mapping={}, result_type=result_type, severity="medium")
