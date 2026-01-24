#!/usr/bin/env python3
import asyncio, sys, os, threading, json, webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

from core.banner import show_banner
from core.help_menu import show_help
from core.scanner import scan_username
from core.correlator import correlate
from core.output import display_results, save_results
from core.colors import Colors, c
from core.network import get_network_settings

# ------------------------------
# Global network/anonymity settings
# ------------------------------
USE_TOR = False
USE_PROXY = False
PROXY_URL = None

# ------------------------------
# Utility functions
# ------------------------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ask(msg: str) -> str:
    try:
        return input(c(msg, Colors.YELLOW)).strip()
    except KeyboardInterrupt:
        print(c("\nInterrupted. Exiting.", Colors.RED))
        sys.exit(0)

def get_anonymity_status() -> str:
    if USE_TOR and USE_PROXY:
        return "Tor + Proxy"
    elif USE_TOR:
        return "Tor only"
    elif USE_PROXY:
        return "Proxy only"
    else:
        return "No anonymization"

# ------------------------------
# Core functionalities
# ------------------------------
async def run_scan(username: str):
    global PROXY_URL
    try:
        PROXY_URL = get_network_settings(USE_PROXY, USE_TOR)
        if PROXY_URL:
            print(c("[+] Network anonymization ENABLED", Colors.GREEN))
    except RuntimeError as e:
        print(c(f"[!] {str(e)}", Colors.RED))
        return

    print(c(f"\nScanning: {username}\n", Colors.CYAN))
    results = await scan_username(username, PROXY_URL)
    correlation = correlate(results)
    display_results(results, correlation)
    save_results(username, results, correlation)

def set_anonymity():
    global USE_TOR, USE_PROXY
    tor_ans = ask("Use Tor? (y/n): ").lower()
    USE_TOR = tor_ans == "y"
    proxy_ans = ask("Use Proxy? (y/n): ").lower()
    USE_PROXY = proxy_ans == "y"

    try:
        _ = get_network_settings(USE_PROXY, USE_TOR)
        print(c("[+] Anonymity settings saved.", Colors.GREEN))
    except RuntimeError as e:
        print(c(f"[!] {str(e)}", Colors.RED))
        USE_TOR = USE_PROXY = False

# ------------------------------
# LIVE DASHBOARD SERVER FUNCTION
# ------------------------------
def launch_live_dashboard(username, port=8000):
    """Launch a live HTML dashboard for a username's scan results."""
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                file_path = f"output/{username}/results.json"
                if not os.path.exists(file_path):
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    msg = f"<h2>No results found for user: {username}</h2>"
                    self.wfile.write(msg.encode())
                    return

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                rows = ""
                for r in data["results"]:
                    status = r["status"]
                    color = "#2ecc71" if status=="FOUND" else "#e74c3c" if status=="ERROR" else "#95a5a6"
                    bio = r.get("bio") or ""
                    bio = bio.replace("\n","<br>")

                    emails = r.get("contacts", {}).get("emails", [])
                    phones = r.get("contacts", {}).get("phones", [])

                    contacts_html = ""
                    if emails:
                        contacts_html += f"<br><strong>Emails:</strong> {', '.join(emails)}"
                    if phones:
                        contacts_html += f"<br><strong>Phones:</strong> {', '.join(phones)}"

                    rows += f"""
                    <tr>
                        <td>{r['platform']}</td>
                        <td style="color:{color}; font-weight:bold;">{status}</td>
                        <td>{r['confidence']}%</td>
                        <td class="bio">{bio}{contacts_html}</td>
                    </tr>
                    """

                correlation_html = ""
                if data.get("correlation"):
                    for bio_text, platforms in data["correlation"].items():
                        bio_preview = bio_text[:120]
                        correlation_html += f"<li><strong>{bio_preview}...</strong> Platforms: {', '.join(platforms)}</li>"
                else:
                    correlation_html = "<li>No correlations found.</li>"

                html_content = f"""
                <html>
                <head>
                    <title>Silica-X Dashboard - {username}</title>
                    <style>
                        body {{ background-color: #0e0e0e; color: #eaeaea; font-family: Arial, sans-serif; padding: 20px; }}
                        h1 {{ color: #00ffff; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        th, td {{ border: 1px solid #333; padding: 10px; text-align: left; vertical-align: top; }}
                        th {{ background-color: #1f1f1f; }}
                        tr:nth-child(even) {{ background-color: #161616; }}
                        .bio {{ max-width: 600px; word-wrap: break-word; font-size: 0.95em; }}
                        .section {{ margin-top: 40px; }}
                        ul {{ margin-top: 10px; }}
                    </style>
                </head>
                <body>
                    <h1>Silica-X Dashboard</h1>
                    <div class="section">
                        <h2>Scan Results</h2>
                        <table>
                            <tr>
                                <th>Platform</th>
                                <th>Status</th>
                                <th>Confidence</th>
                                <th>Bio / Public Info / Contacts</th>
                            </tr>
                            {rows}
                        </table>
                    </div>
                    <div class="section">
                        <h2>Correlation Analysis</h2>
                        <ul>
                            {correlation_html}
                        </ul>
                    </div>
                </body>
                </html>
                """

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html_content.encode())
            else:
                self.send_error(404)

    def run_server():
        server_address = ("", port)
        print(c(f"[+] Dashboard live at http://localhost:{port}/", Colors.GREEN))
        webbrowser.open(f"http://localhost:{port}/")
        with HTTPServer(server_address, Handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] Live dashboard stopped.")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

# ------------------------------
# Main loop
# ------------------------------
async def main():
    clear_screen()
    show_banner(get_anonymity_status())

    while True:
        user_input = ask("Enter command (help / exit): ")

        # EXIT
        if user_input.lower() in ("exit", "quit"):
            print(c("\nExiting Silica-X Now.....!", Colors.RED))
            break

        # HELP
        if user_input.lower() in ("help", "-h", "--help"):
            show_help()
            continue

        # SCAN username
        if user_input.lower().startswith("scan "):
            parts = user_input.split(" ", 1)
            if len(parts) < 2 or not parts[1].strip() or " " in parts[1]:
                print(c("Invalid username.", Colors.RED))
                continue
            username = parts[1].strip()
            await run_scan(username)
            continue

        # ANONYMITY
        if user_input.lower() == "anonymity":
            set_anonymity()
            show_banner(get_anonymity_status())
            continue

        # CLEAR
        if user_input.lower() == "clear":
            clear_screen()
            show_banner(get_anonymity_status())
            continue

        # LIVE DASHBOARD
        if user_input.lower().startswith("live "):
            parts = user_input.split(" ", 1)
            if len(parts) < 2 or not parts[1].strip():
                print(c("Please provide a username. Usage: live <username>", Colors.RED))
                continue
            live_username = parts[1].strip()
            launch_live_dashboard(live_username)
            continue

        # UNKNOWN
        print(c("Unknown command. Type 'help' for options.", Colors.RED))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(c("\nInterrupted. Exiting.", Colors.RED))
        sys.exit(0)
