from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from .faker_compat import create_faker


SCENARIOS = ["Account Takeover", "Synthetic Identity", "Velocity Fraud", "Money Mule Networks", "Promo Abuse"]


@dataclass
class GeneratedBankingData:
    datasets: dict[str, list[dict]]


class BankingDataGenerator:
    def __init__(self, seed: int, output_dir: Path):
        self.seed = seed
        self.output_dir = output_dir
        self.rng = random.Random(seed)
        self.fake = create_faker(seed)
        self.ids = defaultdict(list)

    def generate_all(self, counts: dict[str, int]) -> GeneratedBankingData:
        data = {}
        data["customers"] = self._customers(counts["customers"])
        data["accounts"] = self._accounts(counts["accounts"], data["customers"])
        data["credit_cards"] = self._credit_cards(counts["credit_cards"], data["customers"], data["accounts"])
        data["loans"] = self._loans(counts["loans"], data["customers"], data["accounts"])
        data["merchants"] = self._merchants(counts["merchants"])
        data["devices"] = self._devices(counts["devices"], data["customers"])
        data["sessions"] = self._sessions(counts["sessions"], data["customers"], data["devices"])
        data["behavioral_signals"] = self._behavioral_signals(counts["behavioral_signals"], data["sessions"], data["devices"])
        data["account_openings"] = self._account_openings(counts["account_openings"], data["customers"], data["accounts"])
        data["kyc_documents"] = self._kyc_documents(counts["kyc_documents"], data["customers"])
        data["transactions"] = self._transactions(counts["transactions"], data)
        data["fraud_alerts"] = self._fraud_alerts(counts["fraud_alerts"], data)
        data["fraud_cases"] = self._fraud_cases(counts["fraud_cases"], data)
        data["mule_networks"] = self._mule_networks(counts["mule_networks"], data)
        data["investigations"] = self._investigations(counts["investigations"], data)
        data["approvals"] = self._approvals(counts["approvals"], data)
        data["task_history"] = self._task_history(counts["task_history"], data)
        data["agent_feedback"] = self._agent_feedback(counts["agent_feedback"], data)
        data["knowledge_base"] = self._knowledge_base(counts["knowledge_base"])
        self._write_json(data)
        return GeneratedBankingData(data)

    def _uid(self, prefix: str, n: int) -> str:
        return f"{prefix}_{n:08d}"

    def _date_iso(self, start_days_ago: int = 365) -> str:
        dt = datetime.utcnow() - timedelta(days=self.rng.randint(0, start_days_ago), seconds=self.rng.randint(0, 86400))
        return dt.replace(microsecond=0).isoformat() + "Z"

    def _choice(self, items):
        return items[self.rng.randrange(len(items))]

    def _customers(self, n):
        rows = []
        for i in range(n):
            gender = self._choice(["F", "M", "X"])
            rows.append({
                "customer_id": self._uid("cus", i + 1),
                "full_name": self.fake.name(),
                "gender": gender,
                "date_of_birth": (date.today() - timedelta(days=self.rng.randint(21 * 365, 78 * 365))).isoformat(),
                "email": self.fake.email(),
                "phone": self.fake.phone_number(),
                "address_line1": self.fake.street_address(),
                "city": self.fake.city(),
                "state": self.fake.state(),
                "postal_code": self.fake.postcode(),
                "country": "IN",
                "risk_segment": self._choice(["low", "medium", "high"]),
                "created_at": self._date_iso(1500),
            })
        return rows

    def _accounts(self, n, customers):
        rows = []
        for i in range(n):
            customer = customers[i % len(customers)]
            product = self._choice(["checking", "savings", "salary", "current"])
            opened = datetime.fromisoformat(customer["created_at"].replace("Z", "+00:00"))
            rows.append({
                "account_id": self._uid("acc", i + 1),
                "customer_id": customer["customer_id"],
                "account_number": f"10{self.rng.randint(10**8, 10**9 - 1)}",
                "account_type": product,
                "status": self._choice(["active", "active", "active", "dormant", "frozen"]),
                "currency": "INR",
                "open_date": (opened.date() + timedelta(days=self.rng.randint(1, 120))).isoformat(),
                "branch_code": f"BR{self.rng.randint(100,999)}",
                "balance": round(self.rng.uniform(500, 750000), 2),
                "risk_score": round(self.rng.uniform(0, 1), 4),
            })
        return rows

    def _credit_cards(self, n, customers, accounts):
        rows = []
        for i in range(n):
            customer = customers[i % len(customers)]
            account = accounts[i % len(accounts)]
            rows.append({
                "credit_card_id": self._uid("cc", i + 1),
                "customer_id": customer["customer_id"],
                "account_id": account["account_id"],
                "card_token": f"tok_{self._uid('card', i + 1)}",
                "card_brand": self._choice(["Visa", "Mastercard", "RuPay"]),
                "card_type": self._choice(["debit", "credit"]),
                "status": self._choice(["active", "active", "blocked", "expired"]),
                "credit_limit": round(self.rng.uniform(25000, 1200000), 2),
                "issued_at": self._date_iso(1000),
                "expiry_month": self.rng.randint(1, 12),
                "expiry_year": self.rng.randint(2026, 2032),
            })
        return rows

    def _loans(self, n, customers, accounts):
        rows = []
        for i in range(n):
            customer = self._choice(customers)
            account = self._choice(accounts)
            principal = round(self.rng.uniform(50000, 3500000), 2)
            rows.append({
                "loan_id": self._uid("loan", i + 1),
                "customer_id": customer["customer_id"],
                "account_id": account["account_id"],
                "loan_type": self._choice(["personal", "auto", "home", "education", "business"]),
                "principal_amount": principal,
                "interest_rate": round(self.rng.uniform(7.5, 28.0), 2),
                "tenure_months": self._choice([12, 24, 36, 48, 60, 84, 120, 180, 240]),
                "status": self._choice(["approved", "disbursed", "closed", "delinquent"]),
                "approved_at": self._date_iso(1200),
            })
        return rows

    def _merchants(self, n):
        categories = ["grocery", "travel", "electronics", "fashion", "food_delivery", "utilities", "gaming", "fuel"]
        rows = []
        for i in range(n):
            rows.append({
                "merchant_id": self._uid("mch", i + 1),
                "merchant_name": f"{self.fake.company()} {i+1}",
                "category": self._choice(categories),
                "mcc": self.rng.randint(1000, 9999),
                "city": self.fake.city(),
                "country": "IN",
                "risk_profile": self._choice(["low", "medium", "high"]),
            })
        return rows

    def _devices(self, n, customers):
        rows = []
        for i in range(n):
            customer = customers[i % len(customers)]
            rows.append({
                "device_id": self._uid("dev", i + 1),
                "customer_id": customer["customer_id"],
                "device_type": self._choice(["mobile", "desktop", "tablet"]),
                "os": self._choice(["Android", "iOS", "Windows", "macOS"]),
                "ip_address": f"{self.rng.randint(11, 223)}.{self.rng.randint(0,255)}.{self.rng.randint(0,255)}.{self.rng.randint(1,254)}",
                "geo_city": self.fake.city(),
                "geo_state": self.fake.state(),
                "trusted_device": self.rng.random() < 0.72,
                "first_seen_at": self._date_iso(900),
            })
        return rows

    def _sessions(self, n, customers, devices):
        rows = []
        for i in range(n):
            device = devices[i % len(devices)]
            customer = customers[self.rng.randrange(len(customers))]
            started = datetime.utcnow() - timedelta(days=self.rng.randint(0, 90), minutes=self.rng.randint(0, 3000))
            duration = self.rng.randint(20, 7200)
            rows.append({
                "session_id": self._uid("ses", i + 1),
                "customer_id": customer["customer_id"],
                "device_id": device["device_id"],
                "login_at": started.replace(microsecond=0).isoformat() + "Z",
                "logout_at": (started + timedelta(seconds=duration)).replace(microsecond=0).isoformat() + "Z",
                "channel": self._choice(["web", "mobile_app", "ivr"]),
                "mfa_passed": self.rng.random() < 0.94,
                "session_risk": round(self.rng.uniform(0, 1), 4),
            })
        return rows

    def _behavioral_signals(self, n, sessions, devices):
        rows = []
        signal_types = ["typing_speed", "mouse_jitter", "touch_pressure", "device_entropy", "copy_paste", "navigation_depth"]
        for i in range(n):
            session = sessions[i % len(sessions)]
            device = devices[i % len(devices)]
            rows.append({
                "signal_id": self._uid("sig", i + 1),
                "session_id": session["session_id"],
                "device_id": device["device_id"],
                "signal_type": self._choice(signal_types),
                "signal_value": round(self.rng.uniform(0, 100), 3),
                "captured_at": self._date_iso(90),
            })
        return rows

    def _account_openings(self, n, customers, accounts):
        rows = []
        for i in range(n):
            customer = customers[i % len(customers)]
            account = accounts[i % len(accounts)]
            rows.append({
                "opening_id": self._uid("opn", i + 1),
                "customer_id": customer["customer_id"],
                "account_id": account["account_id"],
                "application_channel": self._choice(["branch", "mobile", "web", "agent"]),
                "status": self._choice(["submitted", "under_review", "approved", "rejected"]),
                "submitted_at": self._date_iso(1200),
            })
        return rows

    def _kyc_documents(self, n, customers):
        doc_types = ["aadhaar", "passport", "pan", "voter_id", "driving_license"]
        rows = []
        for i in range(n):
            customer = customers[i % len(customers)]
            rows.append({
                "kyc_document_id": self._uid("kyc", i + 1),
                "customer_id": customer["customer_id"],
                "document_type": self._choice(doc_types),
                "document_number": f"{self.rng.randint(10**7, 10**12)}",
                "verification_status": self._choice(["verified", "pending", "rejected"]),
                "submitted_at": self._date_iso(1400),
            })
        return rows

    def _transactions(self, n, data):
        accounts = data["accounts"]
        cards = data["credit_cards"]
        merchants = data["merchants"]
        rows = []
        fraud_count = max(1, n // 80)
        fraud_indexes = set(self.rng.sample(range(n), fraud_count))
        for i in range(n):
            from_acc = self._choice(accounts)
            to_acc = self._choice(accounts)
            merchant = self._choice(merchants)
            card = self._choice(cards)
            amount = round(self.rng.uniform(25, 125000), 2)
            scenario = None
            if i in fraud_indexes:
                scenario = self._choice(SCENARIOS)
                amount = round(amount * self.rng.uniform(3, 10), 2)
            rows.append({
                "transaction_id": self._uid("txn", i + 1),
                "account_id": from_acc["account_id"],
                "counterparty_account_id": to_acc["account_id"],
                "credit_card_id": card["credit_card_id"],
                "merchant_id": merchant["merchant_id"],
                "transaction_time": self._date_iso(120),
                "transaction_type": self._choice(["purchase", "transfer", "withdrawal", "bill_pay", "cashback"]),
                "channel": self._choice(["card_present", "ecommerce", "upi", "netbanking", "atm"]),
                "amount": amount,
                "currency": "INR",
                "status": self._choice(["posted", "settled", "reversed", "declined"]),
                "is_fraud_suspected": scenario is not None,
                "fraud_scenario": scenario,
            })
        return rows

    def _fraud_alerts(self, n, data):
        txns = data["transactions"]
        rows = []
        for i in range(n):
            txn = txns[i % len(txns)]
            scenario = txn["fraud_scenario"] or self._choice(SCENARIOS)
            rows.append({
                "fraud_alert_id": self._uid("fra", i + 1),
                "transaction_id": txn["transaction_id"],
                "customer_id": self._choice(data["customers"])["customer_id"],
                "alert_type": scenario,
                "severity": self._choice(["low", "medium", "high", "critical"]),
                "alert_status": self._choice(["open", "triaged", "closed"]),
                "created_at": self._date_iso(60),
            })
        return rows

    def _fraud_cases(self, n, data):
        alerts = data["fraud_alerts"]
        rows = []
        for i in range(n):
            alert = alerts[i % len(alerts)]
            rows.append({
                "fraud_case_id": self._uid("case", i + 1),
                "fraud_alert_id": alert["fraud_alert_id"],
                "customer_id": alert["customer_id"],
                "case_type": alert["alert_type"],
                "case_status": self._choice(["open", "under_review", "confirmed", "false_positive", "closed"]),
                "opened_at": self._date_iso(90),
            })
        return rows

    def _mule_networks(self, n, data):
        customers = data["customers"]
        cases = data["fraud_cases"]
        rows = []
        for i in range(n):
            case = cases[i % len(cases)]
            src = customers[i % len(customers)]
            dst = customers[(i + 7) % len(customers)]
            rows.append({
                "mule_network_id": self._uid("mule", i + 1),
                "fraud_case_id": case["fraud_case_id"],
                "source_customer_id": src["customer_id"],
                "target_customer_id": dst["customer_id"],
                "network_size": self.rng.randint(2, 12),
                "confidence_score": round(self.rng.uniform(0.5, 0.99), 4),
            })
        return rows

    def _investigations(self, n, data):
        cases = data["fraud_cases"]
        rows = []
        for i in range(n):
            case = cases[i % len(cases)]
            rows.append({
                "investigation_id": self._uid("inv", i + 1),
                "fraud_case_id": case["fraud_case_id"],
                "assigned_team": self._choice(["Tier1", "Tier2", "AML", "Forensics"]),
                "priority": self._choice(["P1", "P2", "P3"]),
                "status": self._choice(["open", "in_progress", "escalated", "resolved"]),
                "started_at": self._date_iso(45),
            })
        return rows

    def _approvals(self, n, data):
        invs = data["investigations"]
        rows = []
        for i in range(n):
            inv = invs[i % len(invs)]
            rows.append({
                "approval_id": self._uid("apr", i + 1),
                "investigation_id": inv["investigation_id"],
                "approver_role": self._choice(["analyst", "manager", "risk_lead"]),
                "decision": self._choice(["approve", "reject", "request_more_info"]),
                "approved_at": self._date_iso(30),
            })
        return rows

    def _task_history(self, n, data):
        invs = data["investigations"]
        rows = []
        tasks = ["review", "contact_customer", "check_device", "check_kyc", "escalate", "close_case"]
        for i in range(n):
            inv = invs[i % len(invs)]
            rows.append({
                "task_history_id": self._uid("tsk", i + 1),
                "investigation_id": inv["investigation_id"],
                "task_name": self._choice(tasks),
                "task_status": self._choice(["created", "in_progress", "done", "blocked"]),
                "assigned_to": self._choice(["agent_a", "agent_b", "agent_c", "bot_queue"]),
                "updated_at": self._date_iso(30),
            })
        return rows

    def _agent_feedback(self, n, data):
        rows = []
        for i in range(n):
            rows.append({
                "feedback_id": self._uid("fb", i + 1),
                "task_history_id": data["task_history"][i % len(data["task_history"])]["task_history_id"],
                "agent_id": f"agent_{self.rng.randint(1, 30):03d}",
                "sentiment": self._choice(["positive", "neutral", "negative"]),
                "feedback_text": self.fake.sentence(10),
                "created_at": self._date_iso(10),
            })
        return rows

    def _knowledge_base(self, n):
        rows = []
        for i in range(n):
            rows.append({
                "kb_id": self._uid("kb", i + 1),
                "title": f"{self._choice(['Fraud Playbook', 'Case Note', 'Risk Rule', 'Ops Guide'])} {i+1}",
                "category": self._choice(["fraud", "kyc", "ops", "risk", "payments"]),
                "article_body": self.fake.sentence(20),
                "updated_at": self._date_iso(180),
            })
        return rows

    def _write_json(self, data: dict[str, list[dict]]):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for name, rows in data.items():
            path = self.output_dir / f"{name}.json"
            path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")

