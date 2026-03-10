import mysql.connector
from datetime import date, time, timedelta
import random

# 1. MySQL 연결
conn = mysql.connector.connect(
    host="localhost",
    user="ehpark",
    password="ehPark9463!",
    database="rentcar_db"
)
cursor = conn.cursor()

# 2. 지역별 상세 소스
locations = [
  {"city": "Seoul", "pref": "02", "spots": ["Gasan Digital", "Gangnam Station", "Hongdae", "Yeouido", "Seoul Station", "Jamsil", "Suyu", "Magok"],
   "lat": (37.48, 37.58), "lng": (126.88, 127.05)},
  {"city": "Gyeonggi", "pref": "031", "spots": ["Pangyo", "Suwon Ingye", "Ilsan Lake Park", "Bundang", "Anyang", "Ansan Center", "Pyeongtaek"],
   "lat": (37.25, 37.40), "lng": (126.95, 127.10)},
  {"city": "Busan", "pref": "051", "spots": ["Busan Station", "Haeundae", "Seomyeon", "Gimhae Airport", "Gwangalli", "Dongrae"],
   "lat": (35.10, 35.20), "lng": (129.00, 129.15)},
  {"city": "Incheon", "pref": "032", "spots": ["Incheon Airport T1", "Incheon Airport T2", "Songdo", "Bupyeong", "Guwol-dong"],
   "lat": (37.40, 37.50), "lng": (126.45, 126.70)},
  {"city": "Jeju", "pref": "064", "spots": ["Jeju Airport", "Jeju Auto House", "Jungmun", "Seogwipo Center"],
   "lat": (33.25, 33.50), "lng": (126.30, 126.85)}
]

# 3. 상태값 설정
total_count = 100
statuses = (["ACTIVE"] * 80) + (["PAUSED"] * 10) + (["CLOSED"] * 10)
random.shuffle(statuses)

used_names = set()
used_phones = set()

# 4. 날짜 범위 상수 설정
START_DATE = date(2020, 1, 1)
OPEN_LIMIT_DATE = date(2025, 6, 30)
END_OF_2025 = date(2025, 12, 31)

insert_sql = """
INSERT INTO BRANCH (branch_name, address, latitude, longitude, phone, open_time, close_time, open_date, close_date, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

count = 0
while count < total_count:
  reg = random.choice(locations)
  spot = random.choice(reg['spots'])

  suffix = random.choice(["Center", "Point", "Square", "Office", "Hub", "Station"])
  branch_name = f"{spot} {suffix}"

  if branch_name in used_names: continue
  used_names.add(branch_name)

  address = f"{random.randint(1, 15)}F, {random.randint(10, 800)}, {spot} Road, {reg['city']}, Korea"
  lat = round(random.uniform(reg['lat'][0], reg['lat'][1]), 8)
  lng = round(random.uniform(reg['lng'][0], reg['lng'][1]), 8)

  phone = f"{reg['pref']}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
  if phone in used_phones: continue
  used_phones.add(phone)

  if "Airport" in spot or "Station" in spot:
    open_time = time(random.choice([0, 5, 6]), 0)
    close_time = time(23, 59, 59)
  else:
    open_time = time(random.choice([8, 9, 10]), random.choice([0, 30]))
    close_time = time(random.choice([18, 19, 20, 21, 22]), random.choice([0, 30]))

  # ---------------------------------------------------------
  # ✅ [날짜 로직 수정]
  # ---------------------------------------------------------
  status = statuses[count]

  # 1. open_date: 2020.01.01 ~ 2025.06.30 (균등 분포)
  open_days_range = (OPEN_LIMIT_DATE - START_DATE).days
  open_date = START_DATE + timedelta(days=random.randint(0, open_days_range))

  close_date = None
  # status가 CLOSED인 경우에만 close_date 생성
  if status == "CLOSED":
    # 2. close_date: (open_date + 30일) ~ 2025.12.31
    min_close_date = open_date + timedelta(days=30)

    # 만약 open_date + 30일이 2025.12.31보다 늦으면 범위를 좁힘 (안전 장치)
    if min_close_date > END_OF_2025:
      min_close_date = END_OF_2025 - timedelta(days=1)

    close_days_range = (END_OF_2025 - min_close_date).days
    close_date = min_close_date + timedelta(days=random.randint(0, close_days_range))

  val = (branch_name, address, lat, lng, phone, open_time, close_time, open_date, close_date, status)

  try:
    cursor.execute(insert_sql, val)
    count += 1
  except mysql.connector.Error as e:
    print(f"Error: {e}")
    continue

conn.commit()
print(f"BRANCH data generation completed!")
cursor.close()
conn.close()