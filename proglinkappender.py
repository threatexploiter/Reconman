import json
import os

# === Load existing links.json if exists ===
links_path = "links.json"
existing = []

if os.path.exists(links_path):
    try:
        with open(links_path, 'r') as f:
            existing = json.load(f)
    except Exception as e:
        print(f"[-] Failed to load existing links.json: {e}")
        exit(1)

# === Load new program links from TXT ===
with open("program_links.txt", 'r') as f:
    new_lines = [line.strip() for line in f if line.strip()]

new_entries = []
existing_csv_urls = {entry["CSV"] for entry in existing}

for line in new_lines:
    if "teams/" in line:
        program = line.split("teams/")[-1].split("/")[0]
    else:
        program = line.rstrip("/").split("/")[-1]

    csv_url = f"https://hackerone.com/teams/{program}/assets/download_csv.csv"
    burp_url = f"https://hackerone.com/teams/{program}/assets/download_burp_project_file.json"

    # Skip if already exists
    if csv_url in existing_csv_urls:
        print(f"[~] Skipping duplicate: {program}")
        continue

    new_entries.append({
        "CSV": csv_url,
        "BURP": burp_url
    })
    print(f"[+] Appending: {program}")

# === Save merged list ===
final_links = existing + new_entries

with open(links_path, 'w') as f:
    json.dump(final_links, f, indent=2)

print(f"\n✅ links.json updated. Total programs: {len(final_links)} | Newly added: {len(new_entries)}")
