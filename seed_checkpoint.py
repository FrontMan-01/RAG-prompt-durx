import json

with open("dataset_500.json", "r", encoding="utf-8") as f:
    old_data = json.load(f)

existing_cases = old_data["cases"]
next_case_id = len(existing_cases) + 1

with open("dataset_500_checkpoint.json", "w", encoding="utf-8") as f:
    json.dump({"cases": existing_cases, "case_id": next_case_id}, f, indent=2)

print(f"Seeded checkpoint with {len(existing_cases)} existing cases.")
print(f"Next case_id will start at {next_case_id}")