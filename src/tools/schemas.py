from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | list[Any] | None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CustomerProfileInput(BaseModel):
    customer_id: str


class CustomerNetworkInput(BaseModel):
    customer_id: str


class CustomerRelationshipsInput(BaseModel):
    customer_id: str


class CustomerRiskSummaryInput(BaseModel):
    customer_id: str


class CustomerSearchInput(BaseModel):
    customer_id: str | None = None
    query: str | None = None
    city: str | None = None
    risk_segment: str | None = None


class CustomerContactInfoInput(BaseModel):
    customer_id: str


class CustomerOverviewInput(BaseModel):
    customer_id: str


class CustomerTimelineInput(BaseModel):
    customer_id: str
    days: int | None = 30


class CustomerAccountsInput(BaseModel):
    customer_id: str


class AccountSummaryInput(BaseModel):
    customer_id: str | None = None
    account_id: str | None = None


class AccountBalanceInput(BaseModel):
    customer_id: str | None = None
    account_id: str | None = None


class CreditUtilizationInput(BaseModel):
    customer_id: str


class CustomerExposureInput(BaseModel):
    customer_id: str


class LoanSummaryInput(BaseModel):
    customer_id: str


class CreditCardSummaryInput(BaseModel):
    customer_id: str


class BankingOverviewInput(BaseModel):
    customer_id: str


class RecentTransactionsInput(BaseModel):
    customer_id: str
    days: int | None = 30


class TransactionSearchInput(BaseModel):
    customer_id: str | None = None
    merchant_name: str | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    transaction_type: str | None = None
    status: str | None = None
    days: int | None = 30


class TransactionDetailsInput(BaseModel):
    customer_id: str | None = None
    transaction_id: str


class SpendingSummaryInput(BaseModel):
    customer_id: str
    days: int | None = 30


class SpendingByCategoryInput(BaseModel):
    customer_id: str
    days: int | None = 30


class VelocityMetricsInput(BaseModel):
    customer_id: str
    hours: int | None = 24


class LargeTransactionsInput(BaseModel):
    customer_id: str
    minimum: float | None = 50000
    limit: int | None = 10


class TransactionNetworkInput(BaseModel):
    customer_id: str


class TransactionTimelineInput(BaseModel):
    customer_id: str
    days: int | None = 30


class CustomerDevicesInput(BaseModel):
    customer_id: str


class DeviceProfileInput(BaseModel):
    customer_id: str
    device_id: str


class RecentSessionsInput(BaseModel):
    customer_id: str
    days: int | None = 30


class BehavioralSignalsInput(BaseModel):
    customer_id: str


class DeviceVelocityInput(BaseModel):
    customer_id: str
    hours: int | None = 24


class DeviceHistoryInput(BaseModel):
    customer_id: str
    device_id: str | None = None


class DigitalRiskSummaryInput(BaseModel):
    customer_id: str


class SessionDetailsInput(BaseModel):
    customer_id: str
    session_id: str


class FraudAlertsInput(BaseModel):
    customer_id: str | None = None
    severity: str | None = None
    alert_status: str | None = None


class FraudCaseInput(BaseModel):
    customer_id: str | None = None
    fraud_case_id: str | None = None


class CaseSummaryInput(BaseModel):
    customer_id: str | None = None
    fraud_case_id: str | None = None


class InvestigationPackageInput(BaseModel):
    customer_id: str


class CustomerFraudSummaryInput(BaseModel):
    customer_id: str


class AlertTimelineInput(BaseModel):
    customer_id: str


class MuleNetworkInput(BaseModel):
    customer_id: str


class HighRiskEntitiesInput(BaseModel):
    customer_id: str | None = None
    limit: int | None = 10


class VelocityAnomalyInput(BaseModel):
    customer_id: str
    hours: int | None = 24
    threshold: int | None = 10


class BehavioralAnomalyInput(BaseModel):
    customer_id: str


class CaseDetailsInput(BaseModel):
    investigation_id: str


class CaseTimelineInput(BaseModel):
    investigation_id: str
    customer_id: str | None = None


class ApprovalHistoryInput(BaseModel):
    investigation_id: str


class OpenTasksInput(BaseModel):
    investigation_id: str | None = None
    customer_id: str | None = None


class InvestigationSummaryInput(BaseModel):
    investigation_id: str | None = None
    customer_id: str | None = None


class InvestigationStatusInput(BaseModel):
    investigation_id: str


class RelatedCasesInput(BaseModel):
    customer_id: str


class CaseParticipantsInput(BaseModel):
    investigation_id: str
    customer_id: str | None = None


class AgentFeedbackInput(BaseModel):
    task_history_id: str


class TaskHistoryInput(BaseModel):
    task_name: str


class CustomerInteractionHistoryInput(BaseModel):
    customer_id: str


class ResolutionHistoryInput(BaseModel):
    task_name: str


class AgentLearningExamplesInput(BaseModel):
    task_name: str


class KnowledgeSearchInput(BaseModel):
    query: str


class KnowledgeArticleInput(BaseModel):
    kb_id: str


class OperationalGuidanceInput(BaseModel):
    query: str | None = None


class InvestigationPlaybookInput(BaseModel):
    query: str | None = "investigation playbook"


class FraudProcedureInput(BaseModel):
    query: str | None = "fraud procedure"


class KycGuidanceInput(BaseModel):
    query: str | None = "kyc guidance"

