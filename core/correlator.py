# core/correlator.py

def correlate(results):
    """
    Correlate identical bios across multiple platforms.
    Returns only bios that appear on more than one platform.
    """
    bios = {}

    for r in results:
        if r.get("bio"):
            bios.setdefault(r["bio"], []).append(r["platform"])

    return {bio: platforms for bio, platforms in bios.items() if len(platforms) > 1}
