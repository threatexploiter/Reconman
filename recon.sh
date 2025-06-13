#!/bin/bash

# === Recon Script Based on Your Methodology ===
# Assumes each program folder (e.g., centene_vdp) has roots.txt

TOOLS_DIR=~/tools
THREADS=200
USER_AGENT="GoogleBot"
COOKIE="SESSION=Hacked"

for dir in */; do
    cd "$dir" || continue
    echo "[***] Running recon in: $dir [***]"

    # === DISCOVER SUBDOMAINS ===
    echo "[*] Discovering subdomains..."
    subfinder -dL roots.txt -all -recursive | anew all.txt
    chaos -dL roots.txt | anew chaos.txt

    while IFS= read -r subs; do
        assetfinder -subs-only "$subs" | anew all.txt
    done < roots.txt

    amass enum -df roots.txt -passive | anew all.txt

    cat chaos.txt | grep -v "*" | anew all.txt
    cat chaos.txt | grep "*" | anew wild.txt

    # === VERIFY SUBDOMAINS ===
    echo "[*] Verifying subdomains with httpx..."
    httpx -l all.txt \
        -sc -ports 80,443,8080,8000,8888,8443 \
        -title -asn -cdn -ip -tech-detect \
        -fr -random-agent -vhost -pipeline -http2 \
        -pa -efqdn -favicon -content-length -dashboard \
        -threads $THREADS | anew withdetailalive.txt

    echo "[*] Running Corsy..."
    python3 "$TOOLS_DIR"/Corsy/corsy.py -i all.txt -t 10 \
        --headers "User-Agent: $USER_AGENT\nCookie: $COOKIE" \
        -o corsyres.txt

    # === DIRSEARCH ===
    echo "[*] Running dirsearch on live subdomains..."
    while read -r line; do
        dirsearch -u "https://$line" -x 404,403,429 -i 200 \
            --exclude-sizes 0 -o dirsres.txt
    done < all.txt

    # === KATANA ===
    echo "[*] Crawling with katana..."
    
    katana -list all.txt -d 5 -kf -jc -fx \
        -ef woff,css,png,svg,jpg,woff2,jpeg,gif \
        -o allurls.txt

    # === SecretFinder ===
    echo "[*] Searching secrets in JS files..."
    cat allurls.txt | grep -E "\.js$" >> js.txt
    cat js.txt 2>/dev/null | while read url; do
        python3 "$TOOLS_DIR"/SecretFinder/SecretFinder.py -i "$url" -o cli >> secret.txt
    done

    echo "[+] Recon complete for $dir"
    cd ..
done
