# Schema

## customers
- `customer_id` string
- `full_name` string
- `gender` string
- `date_of_birth` date
- `email` string
- `phone` string
- `address_line1` string
- `city` string
- `state` string
- `postal_code` string
- `country` string
- `risk_segment` string
- `created_at` datetime

## accounts
- `account_id` string
- `customer_id` string
- `account_number` string
- `account_type` string
- `status` string
- `currency` string
- `open_date` date
- `branch_code` string
- `balance` number
- `risk_score` number

## credit_cards
- `credit_card_id` string
- `customer_id` string
- `account_id` string
- `card_token` string
- `card_brand` string
- `card_type` string
- `status` string
- `credit_limit` number
- `issued_at` datetime
- `expiry_month` integer
- `expiry_year` integer

## loans
- `loan_id` string
- `customer_id` string
- `account_id` string
- `loan_type` string
- `principal_amount` number
- `interest_rate` number
- `tenure_months` integer
- `status` string
- `approved_at` datetime

## merchants
- `merchant_id` string
- `merchant_name` string
- `category` string
- `mcc` integer
- `city` string
- `country` string
- `risk_profile` string

## devices
- `device_id` string
- `customer_id` string
- `device_type` string
- `os` string
- `ip_address` string
- `geo_city` string
- `geo_state` string
- `trusted_device` boolean
- `first_seen_at` datetime

## sessions
- `session_id` string
- `customer_id` string
- `device_id` string
- `login_at` datetime
- `logout_at` datetime
- `channel` string
- `mfa_passed` boolean
- `session_risk` number

## behavioral_signals
- `signal_id` string
- `session_id` string
- `device_id` string
- `signal_type` string
- `signal_value` number
- `captured_at` datetime

## account_openings
- `opening_id` string
- `customer_id` string
- `account_id` string
- `application_channel` string
- `status` string
- `submitted_at` datetime

## kyc_documents
- `kyc_document_id` string
- `customer_id` string
- `document_type` string
- `document_number` string
- `verification_status` string
- `submitted_at` datetime

## transactions
- `transaction_id` string
- `account_id` string
- `counterparty_account_id` string
- `credit_card_id` string
- `merchant_id` string
- `transaction_time` datetime
- `transaction_type` string
- `channel` string
- `amount` number
- `currency` string
- `status` string
- `is_fraud_suspected` boolean
- `fraud_scenario` string|null

## fraud_alerts
- `fraud_alert_id` string
- `transaction_id` string
- `customer_id` string
- `alert_type` string
- `severity` string
- `alert_status` string
- `created_at` datetime

## fraud_cases
- `fraud_case_id` string
- `fraud_alert_id` string
- `customer_id` string
- `case_type` string
- `case_status` string
- `opened_at` datetime

## mule_networks
- `mule_network_id` string
- `fraud_case_id` string
- `source_customer_id` string
- `target_customer_id` string
- `network_size` integer
- `confidence_score` number

## investigations
- `investigation_id` string
- `fraud_case_id` string
- `assigned_team` string
- `priority` string
- `status` string
- `started_at` datetime

## approvals
- `approval_id` string
- `investigation_id` string
- `approver_role` string
- `decision` string
- `approved_at` datetime

## task_history
- `task_history_id` string
- `investigation_id` string
- `task_name` string
- `task_status` string
- `assigned_to` string
- `updated_at` datetime

## agent_feedback
- `feedback_id` string
- `task_history_id` string
- `agent_id` string
- `sentiment` string
- `feedback_text` string
- `created_at` datetime

## knowledge_base
- `kb_id` string
- `title` string
- `category` string
- `article_body` string
- `updated_at` datetime

