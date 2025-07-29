# exceptions.py
from typing import List, Any


class ScenarioError(Exception):
    """Base exception for scenario-related errors."""
    pass


class ScenarioNotFoundError(ScenarioError):
    """Raised when a scenario is not found."""
    pass


class PermissionDeniedError(ScenarioError):
    """Raised when user doesn't have permission to access/modify a scenario."""
    pass


class InvalidScenarioStateError(ScenarioError):
    """Raised when trying to perform an operation on a scenario in invalid state."""
    pass


class ValidationError(ScenarioError):
    """Raised when scenario validation fails."""
    def __init__(self, message: str, validation_errors: List[Any] = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []