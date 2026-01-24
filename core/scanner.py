# core/scanner.py
import aiohttp, os, json, asyncio, re
from core.colors import Colors, c
from core.extractor import extract_bio, extract_links

PLATFORM_DIR = "platforms"

# ------------------------------
# Contact extraction helper
# ------------------------------
def extract_contacts(html):
    """Extract emails and phone numbers from HTML content."""
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html)
    phones = re.findall(r'\+?\d[\d\s\-\(\)]{7,}\d', html)
    return {"emails": list(set(emails)), "phones": list(set(phones))}

# ------------------------------
# Scan a single platform
# ------------------------------
async def scan_platform(session, platform_file, username, proxy=None):
    """Scan a single platform JSON and return result dict."""
    p = json.load(open(os.path.join(PLATFORM_DIR, platform_file), encoding="utf-8"))
    url = p["url"].format(username=username)
    platform_name = p.get("name", "UNKNOWN")

    try:
        async with session.get(url, proxy=proxy, timeout=15) as r:
            html = await r.text()
            found = (r.status == p.get("exists_status", 200))

            bio = extract_bio(html) if found else None
            links = extract_links(html) if found else []
            contacts = extract_contacts(html) if found else {}

            conf = int(p.get("confidence_weight", 0) * 100)
            if bio:
                conf += 5
            if contacts["emails"] or contacts["phones"]:
                conf += 5

            print(c(f"[+] {platform_name}: { 'FOUND' if found else 'NOT FOUND' } | Confidence: {min(conf,100)}%", Colors.CYAN))
            return {
                "platform": platform_name,
                "url": url,
                "status": "FOUND" if found else "NOT FOUND",
                "confidence": min(conf, 100),
                "bio": bio,
                "links": links,
                "contacts": contacts
            }

    except Exception as e:
        print(c(f"[!] {platform_name}: ERROR → {str(e)}", Colors.RED))
        return {
            "platform": platform_name,
            "url": url,
            "status": "ERROR",
            "confidence": 0,
            "bio": None,
            "links": [],
            "contacts": {},
            "error": str(e)
        }

# ------------------------------
# Scan username across all platforms
# ------------------------------
async def scan_username(username, proxy=None):
    """Scan a username asynchronously across all platform JSONs."""
    results = []

    print(c(f"\n[INFO] Starting scan for username: {username}", Colors.BLUE))

    async with aiohttp.ClientSession() as session:
        tasks = []
        for f in os.listdir(PLATFORM_DIR):
            if f.endswith(".json"):
                tasks.append(scan_platform(session, f, username, proxy))

        if not tasks:
            print(c("[WARN] No platform JSON files found in platforms/", Colors.YELLOW))
            return []

        results = await asyncio.gather(*tasks)

    print(c(f"[INFO] Scan completed for username: {username}\n", Colors.GREEN))
    return results
