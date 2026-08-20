from __future__ import annotations

import re
from app.models import IdentityConcept

ALIASES: dict[IdentityConcept, list[str]] = {
    IdentityConcept.USERNAME: ["username", "user", "samaccountname", "login", "uid", "accountname"],
    IdentityConcept.EMPLOYEE_ID: ["employeeid", "employee_id", "employeenumber", "matricule", "personnelnumber", "workerid"],
    IdentityConcept.MANAGER: ["manager", "managerid", "supervisor", "responsable"],
    IdentityConcept.EMAIL: ["email", "mail", "userprincipalname", "upn"],
    IdentityConcept.ACCOUNT_TYPE: ["accounttype", "type", "classification", "usertype"],
    IdentityConcept.ACCOUNT_STATUS: ["status", "enabled", "active", "accountstatus", "state"],
    IdentityConcept.DEPARTMENT: ["department", "dept", "division", "service"],
    IdentityConcept.COUNTRY: ["country", "co", "pays"],
    IdentityConcept.LAST_LOGIN: ["lastlogon", "lastlogin", "lastsignindatetime", "last_authentication"],
    IdentityConcept.PRIVILEGE_LEVEL: ["privilege", "privilegelevel", "admin", "isadmin", "risk"],
    IdentityConcept.OWNER: ["owner", "accountowner", "responsible"],
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def infer_concept(column_name: str) -> tuple[IdentityConcept | None, float]:
    normalized = normalize(column_name)
    best: tuple[IdentityConcept | None, float] = (None, 0.0)
    for concept, aliases in ALIASES.items():
        for alias in aliases:
            alias_norm = normalize(alias)
            if normalized == alias_norm:
                return concept, 1.0
            if alias_norm in normalized or normalized in alias_norm:
                best = max(best, (concept, 0.78), key=lambda item: item[1])
    return best


def build_mapping(columns: list[str]) -> dict[str, IdentityConcept]:
    mapping: dict[str, IdentityConcept] = {}
    for column in columns:
        concept, confidence = infer_concept(column)
        if concept and confidence >= 0.75:
            mapping[column] = concept
    return mapping
