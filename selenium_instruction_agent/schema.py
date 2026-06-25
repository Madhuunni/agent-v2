"""Validated JSON schema for browser automation instructions."""

from dataclasses import asdict, dataclass, field
import json
from typing import List, Literal, Optional

Action = Literal["navigate", "type", "click", "verify_visible"]
By = Literal[
    "id", "name", "css selector", "xpath", "link text", "partial link text",
    "tag name", "class name", None,
]
VALID_ACTIONS = {"navigate", "type", "click", "verify_visible"}
VALID_BY = {"id", "name", "css selector", "xpath", "link text", "partial link text", "tag name", "class name", None}


@dataclass
class InstructionStep:
    step_no: int
    action: Action
    element: Optional[str]
    by: By
    selector: Optional[str]
    value: Optional[str]
    value_from_env: Optional[str]
    description: str

    def __post_init__(self) -> None:
        if self.step_no < 1:
            raise ValueError("step_no must be >= 1")
        if self.action not in VALID_ACTIONS:
            raise ValueError(f"invalid action: {self.action}")
        if self.by not in VALID_BY:
            raise ValueError(f"invalid locator strategy: {self.by}")


@dataclass
class InstructionPlan:
    test_name: str
    base_url: Optional[str]
    steps: List[InstructionStep] = field(default_factory=list)

    def model_dump(self) -> dict:
        """Return a JSON-serializable dictionary, matching Pydantic's API name."""
        return asdict(self)

    def model_dump_json(self) -> str:
        """Return valid JSON, matching Pydantic's API name used by tests."""
        return json.dumps(self.model_dump())
