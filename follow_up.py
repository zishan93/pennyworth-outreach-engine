import csv
import smtplib
import time
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
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
FIRST_SENT_FILE = "sent_leads.txt"
FOLLOWUP_LOG_FILE = "followed_up.txt"
DAILY_LIMIT_PER_ACCOUNT = 35

# 1. Load history
if not os.path.exists(FIRST_SENT_FILE):
    print("No initial sent history found.")
    exit()

with open(FIRST_SENT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    first_contacted = set(line.strip().lower() for line in f if line.strip())

followed_up = set()
if os.path.exists(FOLLOWUP_LOG_FILE):
    with open(FOLLOWUP_LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        followed_up = set(line.strip().lower() for line in f if line.strip())

# Just print how many are loaded
print(f"Loaded {len(followed_up)} already followed up.")

# 2. Process CSV
total_limit = DAILY_LIMIT_PER_ACCOUNT * len(ACCOUNTS)
successful_sends = 0
account_index = 0
with open(CSV_FILENAME, mode="r", encoding="utf-8-sig", errors="ignore") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if successful_sends >= total_limit:
            print("Daily limit reached. Stopping.")
            break

        recipient = (
            row.get("EMAIL") or 
            row.get("email") or 
            row.get("Email") or 
            row.get("email_1") or 
            ""
        ).strip().lower()
        company_name = row.get("name") or row.get("Company Name") or "there"

        # Only send if they got Email 1 and have not received Email 2
        if recipient in first_contacted and recipient not in followed_up:
            current_account = ACCOUNTS[account_index % len(ACCOUNTS)]
            account_index += 1
            subject = f"Re: {company_name}"
            body = f"""Hi {company_name},

Floating this back up before the weekend in case it got buried under quotes.

Do you currently have a way to automatically get past domestic and commercial clients rebooking their annual servicing, AC maintenance, and routine system checks, or is it mostly manual chasing?

Happy to send over a quick 2-minute video showing how the client reminder system works for local HVAC contractors if you're curious.

Pennyworth Automations
"""
            msg = MIMEMultipart()
            msg["From"] = f"{current_account['sender_name']} <{current_account['email']}>"
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            try:
                # Open, send, and cleanly close connection per email to prevent timeouts
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
                server.starttls()
                server.login(current_account["email"], current_account["password"])
                server.sendmail(current_account["email"], recipient, msg.as_string())
                server.quit()

                successful_sends += 1
                print(f"[{successful_sends}/{total_limit}] Follow-up sent to {recipient}")

                with open(FOLLOWUP_LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(recipient + "\n")
                followed_up.add(recipient)

                # Delay between sends
                time.sleep(random.randint(45, 75))
            except Exception as e:
                print(f"Failed to follow up with {recipient}: {e}")
                time.sleep(5)

print(f"Done! Total followed up: {successful_sends}")