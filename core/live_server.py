import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

# ------------------------------
# CONFIG
# ------------------------------
PORT = 8000  # You can change this port
USERNAME = ""  # If blank, will ask at runtime

# ------------------------------
# Custom HTTP handler
# ------------------------------
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global USERNAME

        if self.path == "/":
            if not USERNAME:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                msg = "<h2>Please provide username in URL: /?user=<username></h2>"
                self.wfile.write(msg.encode())
                return

            file_path = f"output/{USERNAME}/results.json"
            if not os.path.exists(file_path):
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                msg = f"<h2>No results found for user: {USERNAME}</h2>"
                self.wfile.write(msg.encode())
                return

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())

        else:
            self.send_error(404)

# ------------------------------
# Run server
# ------------------------------
if __name__ == "__main__":
    if not USERNAME:
        USERNAME = input("Enter username to view live results: ").strip()

    server_address = ("", PORT)
    print(f"Serving {USERNAME}'s results at http://localhost:{PORT}/")
    with HTTPServer(server_address, Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
