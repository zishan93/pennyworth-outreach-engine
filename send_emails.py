import csv
import smtplib
import time
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- DUAL SENDER CONFIGURATION ---
ACCOUNTS = [
    {
        "email": "hello@example.COM",
        "password": "YOUR PASSWORD",
        "sender_name": "YOUR NAME"
    },
    {
        "email": "team@example.COM",
        "password": "YOUR PASSWORD",
        "sender_name": "YOUR NAME"
    }
]

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

CSV_FILENAME = "cleaned_leads.csv"
SENT_LOG_FILE = "sent_leads.txt"
DAILY_LIMIT_PER_ACCOUNT = 35  # Sends 70 total per session (35 per mailbox)

# 1. Load sent history to prevent duplicates
contacted_emails = set()
if os.path.exists(SENT_LOG_FILE):
    with open(SENT_LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        contacted_emails = set(line.strip().lower() for line in f if line.strip())

print(f"Loaded {len(contacted_emails)} previously contacted leads.")

total_limit = DAILY_LIMIT_PER_ACCOUNT * len(ACCOUNTS)
successful_sends = 0
account_index = 0

# 2. Process  Leads
with open(CSV_FILENAME, mode="r", encoding="utf-8-sig", errors="ignore") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if successful_sends >= total_limit:
            print(f"Daily limit of {total_limit} reached.")
            break

        # Check all possible email columns Outscraper uses
        recipient = (
            row.get("EMAIL") or
            row.get("email") or
            row.get("Email") or
            row.get("email_1") or
            ""
        ).strip().lower()

        # Check all possible name columns
        company_name = (
            row.get("name") or 
            row.get("name_for_email") or 
            row.get("Company Name") or 
            row.get("query") or 
            ""
        ).strip()

        display_name = company_name if company_name else "there"

        # Validate email
        if not recipient or "@" not in recipient or recipient in contacted_emails:
            continue

        current_sender = ACCOUNTS[account_index % len(ACCOUNTS)]

        subject = f"Quick question regarding past clients for {company_name}"
        body = f"""Hi {company_name},

I noticed your team handles domestic and commercial HVAC installations and servicing in the area.

We set up automated re-engagement systems for local HVAC contractors that bring past clients back for their annual servicing and routine maintenance—without your team having to chase them manually.

Would you be open to a quick 2-minute video showing how the booking system runs?

{current_sender['sender_name']}
"""

        msg = MIMEMultipart()
        msg["From"] = f"{current_sender['sender_name']} <{current_sender['email']}>"
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
            server.starttls()
            server.login(current_sender["email"], current_sender["password"])
            server.sendmail(current_sender["email"], recipient, msg.as_string())
            server.quit()

            successful_sends += 1
            print(f"[{successful_sends}/{total_limit}] Sent via {current_sender['email']} to {recipient}")

            with open(SENT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(recipient + "\n")
            contacted_emails.add(recipient)

            # Alternate to next sender account
            account_index += 1

            # Safe human delay between 45 and 75 seconds
            time.sleep(random.randint(45, 75))

        except Exception as e:
            print(f"Failed sending to {recipient} via {current_sender['email']}: {e}")
            time.sleep(5)

print(f"Finished session! Total sent: {successful_sends}")