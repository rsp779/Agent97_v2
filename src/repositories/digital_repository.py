from __future__ import annotations

from collections import Counter

from src.models.datasets import BehavioralSignal, Device, Session


class DigitalRepository:
    def __init__(self, dal) -> None:
        self.dal = dal

    def get_customer_devices(self, customer_id: str) -> list[Device]:
        return [Device.model_validate(row) for row in self.dal.find("devices", customer_id=customer_id)]

    def get_customer_sessions(self, customer_id: str) -> list[Session]:
        return [Session.model_validate(row) for row in self.dal.find("sessions", customer_id=customer_id)]

    def get_behavioral_profile(self, customer_id: str) -> dict[str, int]:
        sessions = {session.session_id for session in self.get_customer_sessions(customer_id)}
        signals = [row for row in self.dal.load_dataset("behavioral_signals") if row["session_id"] in sessions]
        return dict(Counter(row["signal_type"] for row in signals))

    def get_new_device_events(self, customer_id: str) -> list[Device]:
        return [device for device in self.get_customer_devices(customer_id) if not device.trusted_device]

    def get_device_risk(self, customer_id: str) -> float:
        devices = self.get_customer_devices(customer_id)
        return round(sum(1.0 if not device.trusted_device else 0.2 for device in devices) / len(devices), 3) if devices else 0.0

    def get_session_summary(self, customer_id: str) -> dict[str, int]:
        sessions = self.get_customer_sessions(customer_id)
        return {
            "total": len(sessions),
            "mfa_passed": sum(1 for session in sessions if session.mfa_passed),
            "high_risk": sum(1 for session in sessions if session.session_risk >= 0.7),
        }

