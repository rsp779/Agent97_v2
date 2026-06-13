# Tools

This document describes the production tool layer in `src/tools/`.

## Customer Tools

- `get_customer_profile` - returns one customer profile.
- `get_customer_network` - returns customer-linked accounts, cards, devices, and sessions.
- `get_customer_relationships` - returns a normalized relationship list from the customer network.
- `get_customer_risk_summary` - returns a customer risk view across banking, digital, and transaction signals.
- `search_customer` - searches customers by id, text, city, or risk segment.
- `get_customer_contact_info` - returns contact and address fields for a customer.
- `get_customer_overview` - returns a high-level summary of profile, banking, digital, and fraud context.
- `get_customer_timeline` - returns a combined timeline of transactions, sessions, alerts, cases, and investigations.

## Banking Tools

- `get_customer_accounts` - returns all accounts for a customer.
- `get_account_summary` - returns an account summary by customer or account id.
- `get_account_balance` - returns a balance by customer or account id.
- `get_credit_utilization` - returns credit limit, exposure, and utilization.
- `get_customer_exposure` - returns total customer exposure.
- `get_loan_summary` - returns loan counts and principal totals.
- `get_credit_card_summary` - returns card counts and credit-limit totals.
- `get_banking_overview` - returns a compact banking snapshot.

## Transaction Tools

- `get_recent_transactions` - returns recent transactions for a customer.
- `search_transactions` - searches transactions by customer, merchant, amount, type, status, and time window.
- `get_transaction_details` - returns one transaction by id.
- `get_spending_summary` - returns spending totals and averages.
- `get_spending_by_category` - groups spend by merchant/category proxy.
- `get_velocity_metrics` - returns transaction velocity metrics.
- `get_large_transactions` - returns transactions above a threshold.
- `get_transaction_network` - returns counterparties and merchant frequency.
- `get_transaction_timeline` - returns ordered transaction history.

## Digital Tools

- `get_customer_devices` - returns devices linked to a customer.
- `get_device_profile` - returns one device profile.
- `get_recent_sessions` - returns sessions in a recent time window.
- `get_behavioral_signals` - returns behavioral signal counts for a customer.
- `get_device_velocity` - returns device and session activity measures.
- `get_device_history` - returns a device and session history timeline.
- `get_digital_risk_summary` - returns a digital risk snapshot.
- `get_session_details` - returns one session by id.

## Fraud Tools

- `get_fraud_alerts` - returns alerts with optional severity and status filters.
- `get_fraud_case` - returns a fraud case by id or customer.
- `get_case_summary` - returns case, alert, investigation, and linkage summary.
- `get_investigation_package` - returns the normalized fraud investigation package.
- `get_customer_fraud_summary` - returns a compact fraud summary for one customer.
- `get_alert_timeline` - returns alert history in time order.
- `get_mule_network` - returns mule-network links for a customer.
- `get_high_risk_entities` - returns top alerts and cases.
- `detect_velocity_anomalies` - flags simple transaction velocity anomalies.
- `detect_behavioral_anomalies` - flags simple behavioral anomalies.

## Investigation Tools

- `get_case_details` - returns investigation details by investigation id.
- `get_case_timeline` - returns investigation and approval events in time order.
- `get_approval_history` - returns approval history for an investigation.
- `get_open_tasks` - returns pending or request-more-info tasks.
- `get_investigation_summary` - returns summary by investigation id or customer.
- `get_investigation_status` - returns current investigation status.
- `get_related_cases` - returns all investigations for a customer.
- `get_case_participants` - returns assignee and approver context.

## Memory Tools

- `get_agent_feedback` - returns feedback for a task history record.
- `get_task_history` - returns task history for a task name.
- `get_customer_interaction_history` - returns interaction history tied to the provided identifier.
- `get_resolution_history` - returns successful task pattern counts.
- `get_agent_learning_examples` - returns task history examples plus success counts.

## Knowledge Tools

- `search_knowledge` - searches the knowledge base.
- `get_knowledge_article` - returns a knowledge article by id.
- `retrieve_operational_guidance` - returns operational guidance articles.
- `retrieve_investigation_playbook` - returns investigation playbook content.
- `retrieve_fraud_procedure` - returns fraud procedure guidance.
- `retrieve_kyc_guidance` - returns KYC guidance.

## Registry

- `ALL_TOOLS` - all tool schemas in one collection.
- `get_all_tools(repositories)` - builds every tool definition from one repository bundle.
- `get_customer_tools(repositories)` - builds customer tools.
- `get_banking_tools(repositories)` - builds banking tools.
- `get_transaction_tools(repositories)` - builds transaction tools.
- `get_digital_tools(repositories)` - builds digital tools.
- `get_fraud_tools(repositories)` - builds fraud tools.
- `get_investigation_tools(repositories)` - builds investigation tools.
- `get_memory_tools(repositories)` - builds memory tools.
- `get_knowledge_tools(repositories)` - builds knowledge tools.

## Dependency Injection

- `load_repositories(data_path)` - builds the shared repository bundle.
- `get_tool_services(...)` - returns all tool service objects wired to one repository bundle.

