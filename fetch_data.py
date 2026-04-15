import requests
import pandas as pd
from datetime import datetime
import os

def get_all_records(resource_id):
    url = "https://data.doeb.go.th/api/3/action/datastore_search"
    limit = 100
    offset = 0
    records = []

    while True:
        params = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset
        }
        r = requests.get(url, params=params).json()
        batch = r["result"]["records"]

        if not batch:
            break

        records.extend(batch)
        offset += limit

    return records

records = get_all_records("20fa2d1f-dc42-412d-bd0d-561af04b7d25")
df = pd.DataFrame(records)

today = datetime.today().strftime("%Y-%m-%d")
os.makedirs("output", exist_ok=True)

filename = f"output/รายชื่อผู้ค่ามาตรา_10_{today}.csv"
df.to_csv(filename, index=False, encoding="utf-8-sig")

print("บันทึกไฟล์:", filename)
