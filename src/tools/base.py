from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from pydantic import BaseModel, Field, ValidationError

from .exceptions import RepositoryException, ToolExecutionException
from .schemas import ToolResponse


class RepositoryBundleProtocol(Protocol):
    customer_repository: Any
    banking_repository: Any
    transaction_repository: Any
    digital_repository: Any
    fraud_repository: Any
    investigation_repository: Any
    memory_repository: Any
    knowledge_repository: Any


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    args_schema: type[BaseModel]
    method_name: str


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    args_schema: type[BaseModel]
    service: "BaseToolService"
    method_name: str

    def invoke(self, payload: dict[str, Any] | BaseModel | None = None) -> ToolResponse:
        schema = self.args_schema
        try:
            if payload is None:
                parsed = schema()
            elif isinstance(payload, BaseModel):
                parsed = payload
            else:
                parsed = schema.model_validate(payload)
            method = getattr(self.service, self.method_name)
            return method(parsed)
        except ValidationError as exc:
            return ToolResponse(
                success=False,
                message=str(exc),
                data=None,
                metadata={"tool_name": self.name, "repository_used": "validation", "success": False},
            )

    def __call__(self, payload: dict[str, Any] | BaseModel | None = None) -> ToolResponse:
        return self.invoke(payload)

    def to_langchain_tool(self) -> Any:
        try:
            from langchain_core.tools import StructuredTool
        except Exception:
            return self

        def _run(**kwargs: Any) -> str:
            response = self.invoke(kwargs)
            return response.model_dump_json()

        return StructuredTool.from_function(
            func=_run,
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
        )


class BaseToolService:
    repository_name = "repository"

    def __init__(self, repositories: RepositoryBundleProtocol, logger: logging.Logger | None = None) -> None:
        self.repositories = repositories
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def _metadata(self, tool_name: str, repository_used: str, started: float, success: bool, correlation_id: str) -> dict[str, Any]:
        return {
            "tool_name": tool_name,
            "repository_used": repository_used,
            "execution_ms": round((time.perf_counter() - started) * 1000, 3),
            "success": success,
            "correlation_id": correlation_id,
        }

    def _response(
        self,
        *,
        tool_name: str,
        repository_used: str,
        started: float,
        success: bool,
        message: str,
        data: dict[str, Any] | list[Any] | None = None,
        correlation_id: str,
    ) -> ToolResponse:
        return ToolResponse(
            success=success,
            message=message,
            data=self._normalize(data),
            metadata=self._metadata(tool_name, repository_used, started, success, correlation_id),
        )

    def _normalize(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, list):
            return [self._normalize(item) for item in value]
        if isinstance(value, tuple):
            return [self._normalize(item) for item in value]
        if isinstance(value, dict):
            return {key: self._normalize(item) for key, item in value.items()}
        return value

    def _log_call(self, tool_name: str, correlation_id: str, repository_used: str, success: bool, message: str, started: float) -> None:
        self.logger.info(
            "tool_invocation",
            extra={
                "tool_name": tool_name,
                "repository_used": repository_used,
                "success": success,
                "error_message": None if success else message,
                "correlation_id": correlation_id,
                "execution_ms": round((time.perf_counter() - started) * 1000, 3),
            },
        )

    def _execute(
        self,
        *,
        tool_name: str,
        repository_used: str,
        action: Callable[[], dict[str, Any] | list[Any] | None],
        success_message: str,
    ) -> ToolResponse:
        correlation_id = uuid.uuid4().hex
        started = time.perf_counter()
        try:
            data = action()
            response = self._response(
                tool_name=tool_name,
                repository_used=repository_used,
                started=started,
                success=True,
                message=success_message,
                data=data,
                correlation_id=correlation_id,
            )
            self._log_call(tool_name, correlation_id, repository_used, True, success_message, started)
            return response
        except RepositoryException as exc:
            message = str(exc)
        except Exception as exc:
            message = str(exc)
        response = self._response(
            tool_name=tool_name,
            repository_used=repository_used,
            started=started,
            success=False,
            message=message,
            data=None,
            correlation_id=correlation_id,
        )
        self._log_call(tool_name, correlation_id, repository_used, False, message, started)
        return response

    def _bundle_tools(self, specs: tuple[ToolSpec, ...]) -> list[ToolDefinition]:
        return [ToolDefinition(name=spec.name, description=spec.description, args_schema=spec.args_schema, service=self, method_name=spec.method_name) for spec in specs]

    def _json(self, value: Any) -> str:
        return json.dumps(self._normalize(value), default=str)
