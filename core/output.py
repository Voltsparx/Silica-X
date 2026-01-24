# core/output.py
import os, json
from core.colors import Colors, c
from core.confidence import explain_confidence
from core.html_report import generate_html

def display_results(results, correlation):
    """Display scan results in terminal with colors and confidence reasons."""
    for r in results:
        print(c(r["platform"], Colors.CYAN), r["status"], f"{r['confidence']}%")
        for reason in explain_confidence(r):
            print("  -", reason)

        # Print collected contacts if available
        contacts = r.get("contacts", {})
        if contacts.get("emails"):
            print("  Emails:", ", ".join(contacts["emails"]))
        if contacts.get("phones"):
            print("  Phones:", ", ".join(contacts["phones"]))

def save_results(username, results, correlation):
    """Save results as JSON and generate HTML report."""
    path = f"output/{username}"
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/results.json", "w") as f:
        json.dump({"results": results, "correlation": correlation}, f, indent=2)
    
    html = generate_html(username, results, correlation)
    print(c(f"HTML report saved → {html}", Colors.BLUE))
