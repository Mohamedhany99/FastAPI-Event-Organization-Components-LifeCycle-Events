from __future__ import annotations

import sys
from typing import Optional
from loguru import logger


def configure_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        backtrace=False,
        diagnose=False,
        serialize=False,
        format="<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> | <level>{level}</level> | {message}",
    )


def log_context(
    *,
    contract_number: Optional[str] = None,
    component: Optional[str] = None,
    action: Optional[str] = None,
    created_at: Optional[str] = None,
):
    context = {}
    if contract_number is not None:
        context["contract_number"] = contract_number
    if component is not None:
        context["component"] = component
    if action is not None:
        context["action"] = action
    if created_at is not None:
        context["created_at"] = created_at
    return logger.bind(**context)


