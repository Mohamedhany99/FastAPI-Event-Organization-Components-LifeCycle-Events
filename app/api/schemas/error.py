from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error envelope returned under non-2xx responses.
    """
    code: Literal[
        "not_found",
        "validation_error",
        "conflict",
        "internal_error",
        "forbidden",
        "unauthorized",
        "bad_request",
    ] = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human-readable description of the error")
    details: Optional[Any] = Field(default=None, description="Optional structured details")

    model_config = {"json_schema_extra": {
        "examples": [
            {"code": "not_found", "message": "Contract 1234 not found."},
            {"code": "validation_error", "message": "Invalid payload", "details": {"field": "date", "error": "invalid date"}},
            {"code": "conflict", "message": "Contract already exists"},
        ]
    }}


