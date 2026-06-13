from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.models.datasets import Customer

from .base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, dal) -> None:
        super().__init__(dal, "customers")

    def get_customer(self, customer_id: str) -> Customer | None:
        row = self.get_by_id(customer_id)
        return Customer.model_validate(row) if row else None

    def get_customers(self) -> list[Customer]:
        return [Customer.model_validate(row) for row in self.all()]

    def get_customers_by_city(self, city: str) -> list[Customer]:
        return [Customer.model_validate(row) for row in self.find(city=city)]

    def get_customers_by_segment(self, segment: str) -> list[Customer]:
        return [Customer.model_validate(row) for row in self.find(risk_segment=segment)]

    def get_high_risk_customers(self) -> list[Customer]:
        return [Customer.model_validate(row) for row in self.find(risk_segment="high")]

    def get_customer_network(self, customer_id: str) -> dict[str, Any]:
        customer = self.get_customer(customer_id)
        if customer is None:
            return {}
        return {
            "customer": customer.model_dump(),
            "accounts": self.dal.find("accounts", customer_id=customer_id),
            "cards": self.dal.find("credit_cards", customer_id=customer_id),
            "devices": self.dal.find("devices", customer_id=customer_id),
            "sessions": self.dal.find("sessions", customer_id=customer_id),
        }

