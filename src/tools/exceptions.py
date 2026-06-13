from __future__ import annotations


class ToolException(Exception):
    """Base exception for tool layer failures."""


class ValidationException(ToolException):
    """Raised when tool input validation fails."""


class RepositoryException(ToolException):
    """Raised when a repository call fails."""


class ToolExecutionException(ToolException):
    """Raised when a tool fails during execution."""

