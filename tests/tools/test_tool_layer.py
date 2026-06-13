from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from src.models.datasets import Account, Approval, BehavioralSignal, CreditCard, Customer, Device, FraudAlert, FraudCase, Investigation, KnowledgeBaseEntry, Loan, Session, TaskHistory, Transaction
from src.tools.base import ToolDefinition
from src.tools.registry import get_all_tools


NOW = datetime.now(timezone.utc)


customer = Customer(
    customer_id="cus_1",
    full_name="Jane Doe",
    gender="F",
    date_of_birth=datetime(1990, 1, 1, tzinfo=timezone.utc).date(),
    email="jane@example.com",
    phone="+1-555-0100",
    address_line1="1 Main St",
    city="Mumbai",
    state="MH",
    postal_code="400001",
    country="IN",
    risk_segment="medium",
    created_at=NOW,
)

account = Account(
    account_id="acc_1",
    customer_id="cus_1",
    account_number="0001",
    account_type="savings",
    status="active",
    currency="INR",
    open_date=NOW.date(),
    branch_code="BR01",
    balance=1250.5,
    risk_score=0.2,
)

card = CreditCard(
    credit_card_id="card_1",
    customer_id="cus_1",
    account_id="acc_1",
    card_token="tok_1",
    card_brand="visa",
    card_type="credit",
    status="active",
    credit_limit=5000.0,
    issued_at=NOW,
    expiry_month=12,
    expiry_year=2030,
)

loan = Loan(
    loan_id="loan_1",
    customer_id="cus_1",
    account_id="acc_1",
    loan_type="personal",
    principal_amount=2000.0,
    interest_rate=11.5,
    tenure_months=12,
    status="active",
    approved_at=NOW,
)

transaction = Transaction(
    transaction_id="txn_1",
    account_id="acc_1",
    counterparty_account_id="acc_2",
    credit_card_id="card_1",
    merchant_id="m_1",
    transaction_time=NOW,
    transaction_type="card",
    channel="mobile",
    amount=250.0,
    currency="INR",
    status="posted",
    is_fraud_suspected=False,
    fraud_scenario=None,
)

device = Device(
    device_id="dev_1",
    customer_id="cus_1",
    device_type="mobile",
    os="iOS",
    ip_address="127.0.0.1",
    geo_city="Mumbai",
    geo_state="MH",
    trusted_device=True,
    first_seen_at=NOW,
)

session = Session(
    session_id="ses_1",
    customer_id="cus_1",
    device_id="dev_1",
    login_at=NOW,
    logout_at=NOW,
    channel="app",
    mfa_passed=True,
    session_risk=0.1,
)

alert = FraudAlert(
    fraud_alert_id="fa_1",
    transaction_id="txn_1",
    customer_id="cus_1",
    alert_type="velocity",
    severity="high",
    alert_status="open",
    created_at=NOW,
)

case = FraudCase(
    fraud_case_id="fc_1",
    fraud_alert_id="fa_1",
    customer_id="cus_1",
    case_type="review",
    case_status="open",
    opened_at=NOW,
)

investigation = Investigation(
    investigation_id="inv_1",
    fraud_case_id="fc_1",
    assigned_team="fraud",
    priority="high",
    status="open",
    started_at=NOW,
)

approval = Approval(
    approval_id="ap_1",
    investigation_id="inv_1",
    approver_role="lead",
    decision="request_more_info",
    approved_at=NOW,
)

kb = KnowledgeBaseEntry(
    kb_id="kb_1",
    title="Fraud Playbook",
    category="fraud",
    article_body="Investigate with care.",
    updated_at=NOW,
)

task_history = TaskHistory(
    task_history_id="th_1",
    investigation_id="inv_1",
    task_name="review_case",
    task_status="done",
    assigned_to="agent_1",
    updated_at=NOW,
)


@dataclass
class FakeCustomerRepo:
    should_fail: bool = False

    def get_customer(self, customer_id: str):
        if self.should_fail:
            raise RuntimeError("customer repo failed")
        return customer if customer_id == customer.customer_id else None

    def get_customer_network(self, customer_id: str):
        if self.should_fail:
            raise RuntimeError("customer repo failed")
        return {
            "customer": customer.model_dump(),
            "accounts": [account.model_dump()],
            "cards": [card.model_dump()],
            "devices": [device.model_dump()],
            "sessions": [session.model_dump()],
        }

    def get_customers(self):
        return [customer]


@dataclass
class FakeBankingRepo:
    def get_customer_accounts(self, customer_id: str):
        return [account] if customer_id == customer.customer_id else []

    def get_customer_cards(self, customer_id: str):
        return [card] if customer_id == customer.customer_id else []

    def get_customer_loans(self, customer_id: str):
        return [loan] if customer_id == customer.customer_id else []

    def get_total_balance(self, customer_id: str):
        return 1250.5 if customer_id == customer.customer_id else 0.0

    def get_total_credit_limit(self, customer_id: str):
        return 5000.0 if customer_id == customer.customer_id else 0.0

    def get_total_exposure(self, customer_id: str):
        return 8250.5 if customer_id == customer.customer_id else 0.0


@dataclass
class FakeTransactionRepo:
    def get_customer_transactions(self, customer_id: str):
        return [transaction] if customer_id == customer.customer_id else []

    def get_recent_transactions(self, customer_id: str, days: int = 30):
        return self.get_customer_transactions(customer_id)

    def get_total_spend(self, customer_id: str):
        return 250.0 if customer_id == customer.customer_id else 0.0

    def get_transaction_velocity(self, customer_id: str, hours: int = 24):
        return 1 if customer_id == customer.customer_id else 0

    def get_high_value_transactions(self, customer_id: str, minimum: float = 50000):
        return self.get_customer_transactions(customer_id)


@dataclass
class FakeDigitalRepo:
    def get_customer_devices(self, customer_id: str):
        return [device] if customer_id == customer.customer_id else []

    def get_customer_sessions(self, customer_id: str):
        return [session] if customer_id == customer.customer_id else []

    def get_behavioral_profile(self, customer_id: str):
        return {"typing": 2, "scrolling": 1} if customer_id == customer.customer_id else {}

    def get_device_risk(self, customer_id: str):
        return 0.2 if customer_id == customer.customer_id else 0.0

    def get_session_summary(self, customer_id: str):
        return {"total": 1, "mfa_passed": 1, "high_risk": 0}

    def get_new_device_events(self, customer_id: str):
        return []


@dataclass
class FakeFraudRepo:
    def build_investigation_package(self, customer_id: str):
        return {
            "customer": customer.model_dump(),
            "accounts": [account.model_dump()],
            "transactions": [transaction.model_dump()],
            "devices": [device.model_dump()],
            "sessions": [session.model_dump()],
            "alerts": [alert.model_dump()],
            "cases": [case.model_dump()],
            "investigations": [investigation.model_dump()],
        }

    def get_open_alerts(self):
        return [alert]

    def get_high_risk_alerts(self):
        return [alert]

    def get_customer_cases(self, customer_id: str):
        return [case] if customer_id == customer.customer_id else []

    def get_linked_customers(self, customer_id: str):
        return ["cus_2"] if customer_id == customer.customer_id else []

    def get_mule_network(self, customer_id: str):
        return [{"source_customer_id": customer_id, "target_customer_id": "cus_2"}]


@dataclass
class FakeInvestigationRepo:
    def get_investigation(self, investigation_id: str):
        return investigation if investigation_id == investigation.investigation_id else None

    def get_approval_history(self, investigation_id: str):
        return [approval] if investigation_id == investigation.investigation_id else []

    def get_customer_investigations(self, customer_id: str):
        return [investigation] if customer_id == customer.customer_id else []

    def get_pending_approvals(self, customer_id: str):
        return [approval] if customer_id == customer.customer_id else []


@dataclass
class FakeMemoryRepo:
    def get_agent_feedback(self, task_history_id: str):
        return [{"feedback": "good"}] if task_history_id == "th_1" else []

    def get_similar_tasks(self, task_name: str):
        return [task_history.model_dump()] if task_name == "review_case" else []

    def get_successful_patterns(self):
        return {"review_case": 1}


@dataclass
class FakeKnowledgeRepo:
    def search_documents(self, query: str):
        return [kb.model_dump()] if query else []

    def search_policy(self, query: str):
        return [kb.model_dump()] if query else []


@dataclass
class FakeBundle:
    customer_repository: FakeCustomerRepo
    banking_repository: FakeBankingRepo
    transaction_repository: FakeTransactionRepo
    digital_repository: FakeDigitalRepo
    fraud_repository: FakeFraudRepo
    investigation_repository: FakeInvestigationRepo
    memory_repository: FakeMemoryRepo
    knowledge_repository: FakeKnowledgeRepo


@pytest.fixture
def repositories():
    return FakeBundle(
        customer_repository=FakeCustomerRepo(),
        banking_repository=FakeBankingRepo(),
        transaction_repository=FakeTransactionRepo(),
        digital_repository=FakeDigitalRepo(),
        fraud_repository=FakeFraudRepo(),
        investigation_repository=FakeInvestigationRepo(),
        memory_repository=FakeMemoryRepo(),
        knowledge_repository=FakeKnowledgeRepo(),
    )


def _tool(tools: list[ToolDefinition], name: str) -> ToolDefinition:
    return next(tool for tool in tools if tool.name == name)


def test_customer_profile_success(repositories):
    tool = _tool(get_all_tools(repositories), "get_customer_profile")
    response = tool.invoke({"customer_id": "cus_1"})
    assert response.success is True
    assert response.data["customer_id"] == "cus_1"


def test_invalid_input_returns_safe_response(repositories):
    tool = _tool(get_all_tools(repositories), "get_customer_profile")
    response = tool.invoke({})
    assert response.success is False
    assert response.data is None


def test_repository_failure_is_captured():
    bundle = FakeBundle(
        customer_repository=FakeCustomerRepo(should_fail=True),
        banking_repository=FakeBankingRepo(),
        transaction_repository=FakeTransactionRepo(),
        digital_repository=FakeDigitalRepo(),
        fraud_repository=FakeFraudRepo(),
        investigation_repository=FakeInvestigationRepo(),
        memory_repository=FakeMemoryRepo(),
        knowledge_repository=FakeKnowledgeRepo(),
    )
    tool = _tool(get_all_tools(bundle), "get_customer_network")
    response = tool.invoke({"customer_id": "cus_1"})
    assert response.success is False


def test_empty_results_are_normalized(repositories):
    tool = _tool(get_all_tools(repositories), "search_customer")
    response = tool.invoke({"query": "missing"})
    assert response.success is True
    assert response.data == []


def test_registry_builds_all_tools(repositories):
    tools = get_all_tools(repositories)
    names = {tool.name for tool in tools}
    assert "get_customer_profile" in names
    assert "get_investigation_package" in names
    assert "search_knowledge" in names

