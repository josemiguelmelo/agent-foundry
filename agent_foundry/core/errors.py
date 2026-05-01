"""Shared domain exceptions for CLI orchestration."""

from __future__ import annotations


class AgentFoundryError(Exception):
    """Base exception for predictable application failures."""


class UsageError(AgentFoundryError):
    """Invalid user input or unsupported command usage."""


class ValidationError(AgentFoundryError):
    """Registry or plugin data validation failure."""


class ExternalCommandError(AgentFoundryError):
    """Subprocess execution failure."""


class ConflictError(AgentFoundryError):
    """Install target already exists but is not managed by current plugin."""
