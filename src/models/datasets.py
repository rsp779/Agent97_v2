from __future__ import annotations

from datetime import date, datetime

from .base import AppModel


class Customer(AppModel):
    customer_id: str
    full_name: str
    gender: str
    date_of_birth: date
    email: str
    phone: str
    address_line1: str
    city: str
    state: str
    postal_code: str
    country: str
    risk_segment: str
    created_at: datetime


class Account(AppModel):
    account_id: str
    customer_id: str
    account_number: str
    account_type: str
    status: str
    currency: str
    open_date: date
    branch_code: str
    balance: float
    risk_score: float


class CreditCard(AppModel):
    credit_card_id: str
    customer_id: str
    account_id: str
    card_token: str
    card_brand: str
    card_type: str
    status: str
    credit_limit: float
    issued_at: datetime
    expiry_month: int
    expiry_year: int


class Loan(AppModel):
    loan_id: str
    customer_id: str
    account_id: str
    loan_type: str
    principal_amount: float
    interest_rate: float
    tenure_months: int
    status: str
    approved_at: datetime


class Merchant(AppModel):
    merchant_id: str
    merchant_name: str
    category: str
    mcc: int
    city: str
    country: str
    risk_profile: str


class Device(AppModel):
    device_id: str
    customer_id: str
    device_type: str
    os: str
    ip_address: str
    geo_city: str
    geo_state: str
    trusted_device: bool
    first_seen_at: datetime


class Session(AppModel):
    session_id: str
    customer_id: str
    device_id: str
    login_at: datetime
    logout_at: datetime
    channel: str
    mfa_passed: bool
    session_risk: float


class BehavioralSignal(AppModel):
    signal_id: str
    session_id: str
    device_id: str
    signal_type: str
    signal_value: float
    captured_at: datetime


class AccountOpening(AppModel):
    opening_id: str
    customer_id: str
    account_id: str
    application_channel: str
    status: str
    submitted_at: datetime


class KycDocument(AppModel):
    kyc_document_id: str
    customer_id: str
    document_type: str
    document_number: str
    verification_status: str
    submitted_at: datetime


class Transaction(AppModel):
    transaction_id: str
    account_id: str
    counterparty_account_id: str
    credit_card_id: str
    merchant_id: str
    transaction_time: datetime
    transaction_type: str
    channel: str
    amount: float
    currency: str
    status: str
    is_fraud_suspected: bool
    fraud_scenario: str | None


class FraudAlert(AppModel):
    fraud_alert_id: str
    transaction_id: str
    customer_id: str
    alert_type: str
    severity: str
    alert_status: str
    created_at: datetime


class FraudCase(AppModel):
    fraud_case_id: str
    fraud_alert_id: str
    customer_id: str
    case_type: str
    case_status: str
    opened_at: datetime


class MuleNetwork(AppModel):
    mule_network_id: str
    fraud_case_id: str
    source_customer_id: str
    target_customer_id: str
    network_size: int
    confidence_score: float


class Investigation(AppModel):
    investigation_id: str
    fraud_case_id: str
    assigned_team: str
    priority: str
    status: str
    started_at: datetime


class Approval(AppModel):
    approval_id: str
    investigation_id: str
    approver_role: str
    decision: str
    approved_at: datetime


class TaskHistory(AppModel):
    task_history_id: str
    investigation_id: str
    task_name: str
    task_status: str
    assigned_to: str
    updated_at: datetime


class AgentFeedback(AppModel):
    feedback_id: str
    task_history_id: str
    agent_id: str
    sentiment: str
    feedback_text: str
    created_at: datetime


class KnowledgeBaseEntry(AppModel):
    kb_id: str
    title: str
    category: str
    article_body: str
    updated_at: datetime

