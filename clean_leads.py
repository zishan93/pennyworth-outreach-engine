import csv

input_file = "sample_leads.csv"
output_file = "cleaned_leads.csv"

with open(input_file, mode="r", encoding="utf-8-sig", errors="ignore") as f:
    rows = list(csv.reader(f))

headers = [h.strip() for h in rows[0]]

# Print headers so we can see the exact layout
print("Found columns:", headers)

# Find column index for result or email
result_idx = None
for i, h in enumerate(headers):
    if "result" in h.lower() or "status" in h.lower() or "debounce" in h.lower():
        result_idx = i
        break

clean_rows = rows

with open(output_file, mode="w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(clean_rows)

print(f"Success! Saved {len(clean_rows)-1} leads to {output_file}.")
