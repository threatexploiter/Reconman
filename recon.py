import os
import subprocess

# Base directory containing program folders
base_dir = os.getcwd()

# Loop through all folders in the current directory
for program in os.listdir(base_dir):
    program_path = os.path.join(base_dir, program)
    if not os.path.isdir(program_path):
        continue

    roots_path = os.path.join(program_path, 'roots.txt')
    urls_path = os.path.join(program_path, 'urls.txt')

    if not os.path.exists(roots_path) and not os.path.exists(urls_path):
        print(f"[-] Skipping {program} — no targets found")
        continue

    print(f"\n[***] Starting recon on: {program} [***]")

    # === Run subfinder on roots.txt ===
    if os.path.exists(roots_path):
        sub_out = os.path.join(program_path, 'subdomains.txt')
        cmd_subfinder = f"subfinder -dL \"{roots_path}\" -silent -o \"{sub_out}\""
        print(f"[+] Running: {cmd_subfinder}")
        subprocess.run(cmd_subfinder, shell=True)

    # === Run httpx on subdomains.txt ===
    sub_out = os.path.join(program_path, 'subdomains.txt')
    if os.path.exists(sub_out):
        live_out = os.path.join(program_path, 'live.txt')
        cmd_httpx = f"httpx -l \"{sub_out}\" -silent -o \"{live_out}\""
        print(f"[+] Running: {cmd_httpx}")
        subprocess.run(cmd_httpx, shell=True)

    # === Run nuclei on live.txt ===
    live_out = os.path.join(program_path, 'live.txt')
    if os.path.exists(live_out):
        nuclei_out = os.path.join(program_path, 'nuclei.txt')
        cmd_nuclei = f"nuclei -l \"{live_out}\" -silent -o \"{nuclei_out}\""
        print(f"[+] Running: {cmd_nuclei}")
        subprocess.run(cmd_nuclei, shell=True)
