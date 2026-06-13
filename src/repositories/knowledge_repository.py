from __future__ import annotations


class KnowledgeRepository:
    def __init__(self, dal) -> None:
        self.dal = dal

    def search_documents(self, query: str) -> list[dict]:
        q = query.lower()
        return [row for row in self.dal.load_dataset("knowledge_base") if q in row["title"].lower() or q in row["article_body"].lower()]

    def search_policy(self, query: str) -> list[dict]:
        q = query.lower()
        return [row for row in self.search_documents(query) if row.get("category", "").lower() in {"fraud", "kyc", "ops", "risk"} or q in row["title"].lower()]

    def get_account_opening(self, opening_id: str) -> dict | None:
        return self.dal.get_by_id("account_openings", opening_id)

    def get_customer_openings(self, customer_id: str) -> list[dict]:
        return self.dal.find("account_openings", customer_id=customer_id)

    def get_kyc_documents(self, customer_id: str) -> list[dict]:
        return self.dal.find("kyc_documents", customer_id=customer_id)

