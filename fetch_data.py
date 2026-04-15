import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import pandas as pd
from datetime import datetime
import os


# -------------------------
# CONFIG
# -------------------------
API_URL = "https://data.doeb.go.th/api/3/action/datastore_search"
RESOURCE_ID = "20fa2d1f-dc42-412d-bd0d-561af04b7d25"
LIMIT = 100

HEADERS = {
    "User-Agent": "Mozilla/5.0 (DOEB-Data-Collector; GitHub-Actions)"
}


# -------------------------
# SESSION WITH RETRY
# -------------------------
def create_session_with_retries():
    session = requests.Session()

    retry_strategy = Retry(
        total=3,                    # retry สูงสุด 3 ครั้ง
        backoff_factor=2,           # 2s, 4s, 8s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# -------------------------
# FETCH ALL RECORDS
# -------------------------
def get_all_records(resource_id):
    session = create_session_with_retries()

    offset = 0
    records = []

    while True:
        params = {
            "resource_id": resource_id,
            "limit": LIMIT,
            "offset": offset
        }

        try:
            response = session.get(
                API_URL,
                params=params,
                headers=HEADERS,
                timeout=(10, 60)  # connect 10s, read 60s
            )
            response.raise_for_status()

            data = response.json()
            batch = data["result"]["records"]

            if not batch:
                break

            records.extend(batch)
            offset += LIMIT

        except requests.exceptions.RequestException as e:
            # ✅ สำคัญ: API ล่ม → ออกจากฟังก์ชันอย่างสุภาพ
            print("⚠️ API ใช้งานไม่ได้รอบนี้:")
            print(e)
            return []

    return records


# -------------------------
# MAIN PROCESS
# -------------------------
def main():
    print("เริ่มดึงข้อมูลจาก DOEB API")

    records = get_all_records(RESOURCE_ID)

    if not records:
        print("❌ ไม่พบข้อมูลหรือ API ไม่พร้อมใช้งาน (ข้ามรอบนี้)")
        return  # ❗ ไม่ error เพื่อไม่ให้ GitHub Actions ล้ม

    df = pd.DataFrame.from_records(records)

    # เพิ่ม metadata
    snapshot_date = datetime.today().strftime("%Y-%m-%d")
    df["snapshot_date"] = snapshot_date

    # เตรียมโฟลเดอร์
    os.makedirs("output", exist_ok=True)

    filename = f"output/รายชื่อผู้ค่ามาตรา_10_{snapshot_date}.csv"

    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"✅ บันทึกไฟล์สำเร็จ: {filename}")
    print(f"จำนวนรายการ: {len(df)}")


if __name__ == "__main__":
    main()
