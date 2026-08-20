from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


class IdentityConcept(str, Enum):
    IDENTITY_ID = "IDENTITY_ID"
    ACCOUNT_ID = "ACCOUNT_ID"
    USERNAME = "USERNAME"
    EMPLOYEE_ID = "EMPLOYEE_ID"
    MANAGER = "MANAGER"
    EMAIL = "EMAIL"
    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    ACCOUNT_TYPE = "ACCOUNT_TYPE"
    ACCOUNT_STATUS = "ACCOUNT_STATUS"
    DEPARTMENT = "DEPARTMENT"
    COUNTRY = "COUNTRY"
    LOCATION = "LOCATION"
    CREATION_DATE = "CREATION_DATE"
    LAST_LOGIN = "LAST_LOGIN"
    TERMINATION_DATE = "TERMINATION_DATE"
    ENTITLEMENT = "ENTITLEMENT"
    ROLE = "ROLE"
    PRIVILEGE_LEVEL = "PRIVILEGE_LEVEL"
    SOURCE_SYSTEM = "SOURCE_SYSTEM"
    OWNER = "OWNER"


class Operator(str, Enum):
    equals = "equals"
    not_equals = "not_equals"
    is_empty = "is_empty"
    is_not_empty = "is_not_empty"
    starts_with = "starts_with"
    ends_with = "ends_with"
    contains = "contains"
    not_contains = "not_contains"
    greater_than = "greater_than"
    less_than = "less_than"
    in_ = "in"
    not_in = "not_in"
    matches_regex = "matches_regex"
    is_duplicate = "is_duplicate"
    exists = "exists"
    does_not_exist = "does_not_exist"


class RuleCategory(str, Enum):
    identity_data_quality = "identity_data_quality"
    account_governance = "account_governance"
    account_lifecycle = "account_lifecycle"
    privileged_access = "privileged_access"
    access_governance = "access_governance"
    naming_convention = "naming_convention"
    duplicate_detection = "duplicate_detection"
    data_consistency = "data_consistency"
    custom_business_rule = "custom_business_rule"


ResultType = Literal[
    "compliance_rate", "kpi", "count", "non_compliant_records", "distribution",
    "duplicates", "anomalies", "warning", "custom_query"
]
RuleStatus = Literal["draft", "validated", "rejected", "executed"]
Severity = Literal["low", "medium", "high", "critical"]


class ColumnProfile(BaseModel):
    name: str
    data_type: str
    empty_count: int
    empty_percentage: float
    unique_count: int
    sample_values: list[Any]
    semantic_meaning: IdentityConcept | None = None
    semantic_confidence: float = 0.0


class DatasetProfile(BaseModel):
    dataset_id: str
    filename: str
    total_records: int
    total_columns: int
    columns: list[ColumnProfile]
    field_mapping: dict[str, IdentityConcept]


class RuleCondition(BaseModel):
    field: str
    operator: Operator
    value: Any | None = None
    concept: IdentityConcept | None = None


class CanonicalLogic(BaseModel):
    scope: list[RuleCondition] = Field(default_factory=list)
    assertions: list[RuleCondition] = Field(default_factory=list)
    group_by: str | None = None


class Rule(BaseModel):
    id: str
    name: str
    description: str
    category: RuleCategory
    source_language: str = "en"
    original_input: str = ""
    canonical_logic: CanonicalLogic
    dataset_field_mapping: dict[str, str] = Field(default_factory=dict)
    conditions: list[RuleCondition] = Field(default_factory=list)
    expected_result: dict[str, Any] = Field(default_factory=dict)
    result_type: ResultType = "non_compliant_records"
    status: RuleStatus = "draft"
    severity: Severity = "medium"
    enabled: bool = True


class RuleExecutionResult(BaseModel):
    rule_id: str
    rule_name: str
    result_type: ResultType
    total_scoped_records: int
    compliant_count: int | None = None
    non_compliant_count: int | None = None
    compliance_rate: float | None = None
    count: int | None = None
    distribution: dict[str, int] | None = None
    records: list[dict[str, Any]] = Field(default_factory=list)
    insight: str
