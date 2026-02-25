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

# 2. 지역별 상세 소스 (랜드마크와 상세 동네 이름 조합)
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

# 3. 상태값 비율 (80:10:10)
total_count = 100
statuses = (["ACTIVE"] * 80) + (["PAUSED"] * 10) + (["CLOSED"] * 10)
random.shuffle(statuses)

# 중복 체크용 셋
used_names = set()
used_phones = set()

# 4. 데이터 생성 루프
insert_sql = """
INSERT INTO BRANCH (branch_name, address, latitude, longitude, phone, open_time, close_time, open_date, close_date, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

count = 0
while count < total_count:
  reg = random.choice(locations)
  spot = random.choice(reg['spots'])

  # 1. 지점명 생성 (지명 + 수식어 조합으로 중복 방지)
  suffix = random.choice(["Center", "Point", "Square", "Office", "Hub", "Station"])
  branch_name = f"{spot} {suffix}"

  if branch_name in used_names: continue  # 중복 시 재생성
  used_names.add(branch_name)

  # 2. 주소 생성
  address = f"{random.randint(1, 15)}F, {random.randint(10, 800)}, {spot} Road, {reg['city']}, Korea"

  # 3. 위경도
  lat = round(random.uniform(reg['lat'][0], reg['lat'][1]), 8)
  lng = round(random.uniform(reg['lng'][0], reg['lng'][1]), 8)

  # 4. 전화번호 (지역번호 유지하며 중복 방지)
  phone = f"{reg['pref']}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
  if phone in used_phones: continue
  used_phones.add(phone)

  # 5. 영업시간 (지점별 다양화)
  # 공항이나 역세권은 일찍 열고 늦게 닫음
  if "Airport" in spot or "Station" in spot:
    open_time = time(random.choice([0, 5, 6]), 0)
    close_time = time(23, 59, 59)
  else:
    open_time = time(random.choice([8, 9, 10]), random.choice([0, 30]))
    close_time = time(random.choice([18, 19, 20, 21, 22]), random.choice([0, 30]))

  # 6. 운영 날짜 및 상태
  status = statuses[count]
  open_date = date(2020, 1, 1) + timedelta(days=random.randint(0, 2500))
  close_date = None
  if status == "CLOSED":
    close_date = open_date + timedelta(days=random.randint(365, 1000))

  val = (branch_name, address, lat, lng, phone, open_time, close_time, open_date, close_date, status)

  try:
    cursor.execute(insert_sql, val)
    count += 1
  except mysql.connector.Error:
    continue

conn.commit()
print(f"BRANCH data generation completed!")
cursor.close()
conn.close()