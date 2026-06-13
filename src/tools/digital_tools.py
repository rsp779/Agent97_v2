from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    BehavioralSignalsInput,
    CustomerDevicesInput,
    DeviceHistoryInput,
    DeviceProfileInput,
    DeviceVelocityInput,
    DigitalRiskSummaryInput,
    RecentSessionsInput,
    SessionDetailsInput,
)
from .schemas import ToolResponse


DIGITAL_TOOL_SPECS = (
    ToolSpec("get_customer_devices", "Return devices for a customer.", CustomerDevicesInput, "get_customer_devices"),
    ToolSpec("get_device_profile", "Return a device profile.", DeviceProfileInput, "get_device_profile"),
    ToolSpec("get_recent_sessions", "Return recent customer sessions.", RecentSessionsInput, "get_recent_sessions"),
    ToolSpec("get_behavioral_signals", "Return behavioral signal counts.", BehavioralSignalsInput, "get_behavioral_signals"),
    ToolSpec("get_device_velocity", "Return device and session velocity.", DeviceVelocityInput, "get_device_velocity"),
    ToolSpec("get_device_history", "Return device history.", DeviceHistoryInput, "get_device_history"),
    ToolSpec("get_digital_risk_summary", "Return a digital risk summary.", DigitalRiskSummaryInput, "get_digital_risk_summary"),
    ToolSpec("get_session_details", "Return a session detail record.", SessionDetailsInput, "get_session_details"),
)


class DigitalTools(BaseToolService):
    repository_name = "digital_repository"

    def _devices(self, customer_id: str):
        return self.repositories.digital_repository.get_customer_devices(customer_id)

    def _sessions(self, customer_id: str):
        return self.repositories.digital_repository.get_customer_sessions(customer_id)

    def get_customer_devices(self, input: CustomerDevicesInput) -> ToolResponse:
        """Return customer devices."""

        return self._execute(
            tool_name="get_customer_devices",
            repository_used=self.repository_name,
            success_message="customer devices retrieved",
            action=lambda: [device.model_dump() for device in self._devices(input.customer_id)],
        )

    def get_device_profile(self, input: DeviceProfileInput) -> ToolResponse:
        """Return a single device profile."""

        def action() -> dict[str, Any]:
            for device in self._devices(input.customer_id):
                if device.device_id == input.device_id:
                    return device.model_dump()
            return {}

        return self._execute(
            tool_name="get_device_profile",
            repository_used=self.repository_name,
            success_message="device profile retrieved",
            action=action,
        )

    def get_recent_sessions(self, input: RecentSessionsInput) -> ToolResponse:
        """Return recent sessions."""

        def action() -> list[dict[str, Any]]:
            cutoff = datetime.now(timezone.utc) - timedelta(days=input.days or 30)
            return [session.model_dump() for session in self._sessions(input.customer_id) if session.login_at >= cutoff]

        return self._execute(
            tool_name="get_recent_sessions",
            repository_used=self.repository_name,
            success_message="recent sessions retrieved",
            action=action,
        )

    def get_behavioral_signals(self, input: BehavioralSignalsInput) -> ToolResponse:
        """Return behavioral signal counts."""

        return self._execute(
            tool_name="get_behavioral_signals",
            repository_used=self.repository_name,
            success_message="behavioral signals retrieved",
            action=lambda: self.repositories.digital_repository.get_behavioral_profile(input.customer_id),
        )

    def get_device_velocity(self, input: DeviceVelocityInput) -> ToolResponse:
        """Return a device velocity summary."""

        def action() -> dict[str, Any]:
            devices = self._devices(input.customer_id)
            sessions = self._sessions(input.customer_id)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=input.hours or 24)
            return {
                "customer_id": input.customer_id,
                "device_count": len(devices),
                "session_count": len([session for session in sessions if session.login_at >= cutoff]),
                "risk_score": self.repositories.digital_repository.get_device_risk(input.customer_id),
            }

        return self._execute(
            tool_name="get_device_velocity",
            repository_used=self.repository_name,
            success_message="device velocity retrieved",
            action=action,
        )

    def get_device_history(self, input: DeviceHistoryInput) -> ToolResponse:
        """Return a device history timeline."""

        def action() -> list[dict[str, Any]]:
            events: list[dict[str, Any]] = []
            for device in self._devices(input.customer_id):
                if input.device_id and device.device_id != input.device_id:
                    continue
                events.append({"type": "device", "id": device.device_id, "ts": device.first_seen_at, "trusted_device": device.trusted_device})
            for session in self._sessions(input.customer_id):
                if input.device_id and session.device_id != input.device_id:
                    continue
                events.append({"type": "session", "id": session.session_id, "ts": session.login_at, "device_id": session.device_id, "mfa_passed": session.mfa_passed})
            events.sort(key=lambda row: str(row.get("ts", "")))
            return events

        return self._execute(
            tool_name="get_device_history",
            repository_used=self.repository_name,
            success_message="device history retrieved",
            action=action,
        )

    def get_digital_risk_summary(self, input: DigitalRiskSummaryInput) -> ToolResponse:
        """Return a digital risk summary."""

        def action() -> dict[str, Any]:
            return {
                "customer_id": input.customer_id,
                "device_risk": self.repositories.digital_repository.get_device_risk(input.customer_id),
                "session_summary": self.repositories.digital_repository.get_session_summary(input.customer_id),
                "behavioral_profile": self.repositories.digital_repository.get_behavioral_profile(input.customer_id),
                "new_device_events": [device.model_dump() for device in self.repositories.digital_repository.get_new_device_events(input.customer_id)],
            }

        return self._execute(
            tool_name="get_digital_risk_summary",
            repository_used=self.repository_name,
            success_message="digital risk summary retrieved",
            action=action,
        )

    def get_session_details(self, input: SessionDetailsInput) -> ToolResponse:
        """Return a single session detail record."""

        def action() -> dict[str, Any]:
            for session in self._sessions(input.customer_id):
                if session.session_id == input.session_id:
                    return session.model_dump()
            return {}

        return self._execute(
            tool_name="get_session_details",
            repository_used=self.repository_name,
            success_message="session details retrieved",
            action=action,
        )

