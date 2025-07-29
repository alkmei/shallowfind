from http import HTTPStatus
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel


T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format."""
    success: bool = True
    data: T
    message: str
    status_code: int = HTTPStatus.OK


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    message: str
    error: Optional[str] = None
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR


class ValidationErrorResponse(BaseModel):
    """Response format for validation errors."""
    success: bool = False
    message: str
    validation_errors: List[Any] = []
    status_code: int = HTTPStatus.BAD_REQUEST