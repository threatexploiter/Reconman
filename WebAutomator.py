import os
import csv
import requests
import re
import json

# === Load All Programs from links.json ===
programs = []
current = {}

try:
    with open("links.json", 'r') as f:
        programs = json.load(f)
except Exception as e:
    print(f"[-] Failed to load JSON: {e}")
    exit(1)

if not programs or not isinstance(programs, list):
    print("[-] No valid program entries found in links.json")
    exit(1)

# === Process Each Program ===
for prog in programs:
    csv_url = prog['CSV']
    burp_url = prog['BURP']

    # Extract program name
    match = re.search(r'teams/([^/]+)/', csv_url)
    if not match:
        print(f"[-] Could not extract program name from: {csv_url}")
        continue

    program_name = match.group(1)
    base_dir = os.path.join(os.getcwd(), program_name)
    def notify_discord(msg):
        webhook = "your-discord-webhook"
        try:
            requests.post(webhook, json={"content": msg})
        except:
            print("[!] Failed to send Discord notification")

    # === Skip if already processed ===
    if os.path.exists(base_dir):
        expected_files = ['scope.csv', 'burp_config.json', 'roots.txt', 'urls.txt', 'other.txt']
        files_found = [f for f in expected_files if os.path.exists(os.path.join(base_dir, f))]
        if not len(files_found) >=3:
            notify_discord(f"[+] Info Gathered for {program_name} 🎯")
        if len(files_found) >= 3:
            print(f"[~] Skipping {program_name} — already processed ({len(files_found)} files)")
            continue

    os.makedirs(base_dir, exist_ok=True)


    print(f"\n[***] Processing program: {program_name} [***]")

    # === Download CSV ===
    csv_path = os.path.join(base_dir, "scope.csv")
    try:
        resp = requests.get(csv_url)
        if resp.status_code == 200:
            with open(csv_path, 'wb') as f:
                f.write(resp.content)
            print(f"[+] CSV downloaded: {csv_path}")
        else:
            print(f"[-] Failed to download CSV for {program_name}")
            continue
    except Exception as e:
        print(f"[-] CSV error for {program_name}: {e}")
        continue

    # === Download BURP ===
    burp_path = os.path.join(base_dir, "burp_config.json")
    try:
        resp = requests.get(burp_url)
        if resp.status_code == 200:
            with open(burp_path, 'wb') as f:
                f.write(resp.content)
            print(f"[+] BURP config downloaded: {burp_path}")
        else:
            print(f"[-] Failed to download BURP config for {program_name}")
    except Exception as e:
        print(f"[-] BURP download error for {program_name}: {e}")

    # === Parse CSV ===
    wildcards, urls, others = set(), set(), set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            asset_type = row.get('asset_type', '').lower()
            asset_id = row.get('identifier', '').strip()

            if not asset_id:
                continue

            # Normalize the asset_id
            asset_id = asset_id.replace("https://", "").replace("http://", "").strip("/")

            if asset_type == 'wildcard':
                clean_domain = asset_id.lstrip('*.')  # removes "*." if present
                wildcards.add(clean_domain)
            elif asset_type == 'url':
                urls.add(asset_id)
            else:
                others.add(asset_id)



    # === Save Parsed Scopes ===
    def save_list(name, data):
        path = os.path.join(base_dir, name)
        with open(path, 'w') as f:
            for item in sorted(data):
                f.write(item + '\n')
        print(f"[+] {name} saved ({len(data)} items)")
            

    save_list("roots.txt", wildcards)
    save_list("urls.txt", urls)
    save_list("other.txt", others)

    




# we have to make a directory in the current directory of the program name
# we have to then get the csv file and then the burp config file from the links and download it
# then we have to get the wildcards in roots.txt and urls in urls.txt and other stuff in other.txt
# program link https://hackerone.com/hubspot/policy_scopes
# burp project link https://hackerone.com/teams/alibaba_vdp/assets/download_burp_project_file.json
# csv file link https://hackerone.com/teams/hubspot/assets/download_csv.csv
# after that we have to run our own recon script then we have to send stuff to discord that our recon has been done.
# these are all public programs so the link is accessible