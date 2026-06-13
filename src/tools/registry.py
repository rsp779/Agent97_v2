from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .banking_tools import BANKING_TOOL_SPECS, BankingTools
from .base import ToolDefinition, ToolSpec
from .customer_tools import CUSTOMER_TOOL_SPECS, CustomerTools
from .digital_tools import DIGITAL_TOOL_SPECS, DigitalTools
from .fraud_tools import FRAUD_TOOL_SPECS, FraudTools
from .investigation_tools import INVESTIGATION_TOOL_SPECS, InvestigationTools
from .knowledge_tools import KNOWLEDGE_TOOL_SPECS, KnowledgeTools
from .memory_tools import MEMORY_TOOL_SPECS, MemoryTools
from .transaction_tools import TRANSACTION_TOOL_SPECS, TransactionTools


CUSTOMER_TOOLS = CUSTOMER_TOOL_SPECS
BANKING_TOOLS = BANKING_TOOL_SPECS
TRANSACTION_TOOLS = TRANSACTION_TOOL_SPECS
DIGITAL_TOOLS = DIGITAL_TOOL_SPECS
FRAUD_TOOLS = FRAUD_TOOL_SPECS
INVESTIGATION_TOOLS = INVESTIGATION_TOOL_SPECS
MEMORY_TOOLS = MEMORY_TOOL_SPECS
KNOWLEDGE_TOOLS = KNOWLEDGE_TOOL_SPECS

ALL_TOOLS = (
    *CUSTOMER_TOOLS,
    *BANKING_TOOLS,
    *TRANSACTION_TOOLS,
    *DIGITAL_TOOLS,
    *FRAUD_TOOLS,
    *INVESTIGATION_TOOLS,
    *MEMORY_TOOLS,
    *KNOWLEDGE_TOOLS,
)


def _build(service: Any, specs: tuple[ToolSpec, ...]) -> list[ToolDefinition]:
    return [ToolDefinition(name=spec.name, description=spec.description, args_schema=spec.args_schema, service=service, method_name=spec.method_name) for spec in specs]


def get_customer_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(CustomerTools(repositories), CUSTOMER_TOOLS)


def get_banking_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(BankingTools(repositories), BANKING_TOOLS)


def get_transaction_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(TransactionTools(repositories), TRANSACTION_TOOLS)


def get_digital_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(DigitalTools(repositories), DIGITAL_TOOLS)


def get_fraud_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(FraudTools(repositories), FRAUD_TOOLS)


def get_investigation_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(InvestigationTools(repositories), INVESTIGATION_TOOLS)


def get_memory_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(MemoryTools(repositories), MEMORY_TOOLS)


def get_knowledge_tools(repositories: Any) -> list[ToolDefinition]:
    return _build(KnowledgeTools(repositories), KNOWLEDGE_TOOLS)


def get_all_tools(repositories: Any) -> list[ToolDefinition]:
    tools: list[ToolDefinition] = []
    tools.extend(get_customer_tools(repositories))
    tools.extend(get_banking_tools(repositories))
    tools.extend(get_transaction_tools(repositories))
    tools.extend(get_digital_tools(repositories))
    tools.extend(get_fraud_tools(repositories))
    tools.extend(get_investigation_tools(repositories))
    tools.extend(get_memory_tools(repositories))
    tools.extend(get_knowledge_tools(repositories))
    return tools

