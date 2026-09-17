import csv
import os

FIRST_SENT_FILE = "sent_leads.txt"
FOLLOWUP_LOG_FILE = "followed_up.txt"

# Change this to whatever CSV you want to audit ("hvac_ready.csv" or "sheffield_100-debounce.csv")
CSV_FILENAME = "cleaned_leads.csv"

def load_set(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        return set(line.strip().lower() for line in f if line.strip())

first_sent = load_set(FIRST_SENT_FILE)
followed_up = load_set(FOLLOWUP_LOG_FILE)

uncontacted = []
needs_followup = []
completed = []

if not os.path.exists(CSV_FILENAME):
    print(f"Error: {CSV_FILENAME} not found.")
    exit()

with open(CSV_FILENAME, mode="r", encoding="utf-8-sig", errors="ignore") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (
            row.get("EMAIL") or 
            row.get("email") or 
            row.get("Email") or 
            row.get("email_1") or 
            ""
        ).strip().lower()

        name = row.get("name") or row.get("company_name") or row.get("Company Name") or "Unknown"

        if not email:
            continue

        if email in followed_up:
            completed.append((name, email))
        elif email in first_sent:
            needs_followup.append((name, email))
        else:
            uncontacted.append((name, email))

print("=" * 55)
print(f"PIPELINE AUDIT FOR: {CSV_FILENAME}")
print("=" * 55)
print(f"1. Up Next (Uncontacted):     {len(uncontacted)}")
print(f"2. Needs Follow-up:           {len(needs_followup)}")
print(f"3. Fully Completed (Sent 1+2):{len(completed)}")
print("=" * 55)

if needs_followup:
    print("\n--- [NEEDS FOLLOW-UP] (Next 5 shown) ---")
    for n, e in needs_followup[:5]:
        print(f"  • {n} -> {e}")

if uncontacted:
    print("\n--- [UP NEXT FOR COLD OUTREACH] (Next 5 shown) ---")
    for n, e in uncontacted[:5]:
        print(f"  • {n} -> {e}")