from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class FailureCategory(str, Enum):
    environment = "environment"
    flaky_test = "flaky_test"
    assertion_failure = "assertion_failure"
    compilation_error = "compilation_error"
    dependency = "dependency"
    timeout = "timeout"
    infrastructure = "infrastructure"
    unknown = "unknown"


class ReleaseRisk(str, Enum):
    blocker = "blocker"
    high = "high"
    medium = "medium"
    low = "low"


class SuggestedAction(BaseModel):
    title: str
    description: str
    priority: int = Field(ge=1, le=5, description="1=highest priority")


class TriageReport(BaseModel):
    failure_summary: str = Field(description="One-sentence summary of the failure")
    root_cause: str = Field(description="Detailed root cause analysis")
    category: FailureCategory
    severity: Severity
    affected_component: str = Field(description="The component, module, or service that failed")
    is_flaky: bool = Field(description="Whether this appears to be a flaky/non-deterministic failure")
    suggested_actions: list[SuggestedAction] = Field(
        description="Ordered list of recommended fixes or investigation steps"
    )
    predicted_owner: str = Field(
        description="Team or individual most likely responsible, based on the failure"
    )
    similar_failure_patterns: list[str] = Field(
        description="Known patterns this failure resembles"
    )
    release_risk: ReleaseRisk = Field(
        description="Assessment of risk to shipping if this is not fixed"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for this analysis")
