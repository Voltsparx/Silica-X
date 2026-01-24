import os
import csv

def save_csv(username, results):
    path = f"output/{username}"
    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/report.csv"

    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Platform", "Status", "Confidence", "Bio / Public Info"])
        for r in results:
            bio = r.get("bio") or ""
            writer.writerow([r["platform"], r["status"], r["confidence"], bio])

    return file_path
