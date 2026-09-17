# pennyworth-outreach-engine
A modular, batch-processing outbound automation and lead management engine built in Python. Designed to handle data sanitisation, multi-inbox load balancing, domain reputation protection, and state tracking.

## System Architecture

* **`clean_leads.py`**: Ingestion and sanitisation pipeline. Strips formatting anomalies, normalises contact structures, and outputs clean batch files.
* **`send_emails.py`**: Outbound delivery engine configured with dual-inbox rotation (`hello@` and `team@`). Enforces strict rate limits (35 emails/account/day) to safeguard domain deliverability.
* **`follow_up.py`**: Automated follow-up sequencing that checks historical contact logs and prevents duplicate sends.
* **`tracker.py`**: State machine audit script. Cross-references target lead files against delivery logs to categorise contacts into `uncontacted`, `needs follow-up`, and `completed`.

## Deliverability & Infrastructure Design

* **Inbox Rotation**: Distributes volume across multiple authenticated SMTP accounts to prevent spam-filter flagging.
* **Idempotency & Deduplication**: State files (`sent_leads.txt`, `followed_up.txt`) prevent accidental duplicate sends across runs.
* **Fault-Tolerant Parsing**: Handles mixed UTF-8 encodings and malformed CSV rows during lead ingestion.

## Setup & Execution

1. Clone repository:
   git clone https://github.com/zishan93/pennyworth-outreach-engine.git

2. Clean raw prospect batches:
   python clean_leads.py

3. Run outbound dispatch:
   python send_emails.py

4. Audit pipeline status:
   python tracker.py

Note: Production credentials and client data have been and  with prop data for security and privacy.
