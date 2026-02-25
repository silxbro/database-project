import mysql.connector
import random
from datetime import datetime, timedelta

# 1. DB 연결
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
)
cursor = conn.cursor(dictionary=True)

# 2. 기준 정보 설정
TODAY = datetime.now()
BATCH_SIZE = 100000

# 3. 사고 유형 (Short & Clear)
ACCIDENT_TYPES = [
  'COLLISION', 'SELF_DAMAGE', 'REAR_END', 'SIDE_SWIPE',
  'PARKING', 'VIOLATION', 'PEDESTRIAN', 'TIRE/WHEEL'
]

# 4. 한국 주요 도로명 및 지역구 데이터 (English)
ROADS = [
  'Teheran-ro', 'Gangnam-daero', 'Banpo-daero', 'Olympic-ro', 'Dosan-daero',
  'Mapo-daero', 'Yanghwa-ro', 'Saemunan-ro', 'Sejong-daero', 'Gyeongbu Expressway'
]
DISTRICTS = [
  'Gangnam-gu', 'Seocho-gu', 'Songpa-gu', 'Mapo-gu', 'Jongno-gu',
  'Yeongdeungpo-gu', 'Yongsan-gu', 'Seongdong-gu', 'Gangdong-gu'
]
CITIES = ['Seoul', 'Incheon', 'Suwon', 'Busan', 'Daegu']

# 5. 대상 RENTAL 데이터 가져오기 (RETURNED, RENTING)
print("Loading RENTAL information...")
cursor.execute("""
    SELECT rental_id, start_date, end_date, return_date, status 
    FROM RENTAL 
    WHERE status IN ('RETURNED', 'RENTING')
""")
rentals = cursor.fetchall()

def generate_random_datetime(start_date, end_date):
  start_dt = datetime.combine(start_date, datetime.min.time())
  end_dt = datetime.combine(end_date, datetime.max.time())
  delta = end_dt - start_dt
  if delta.total_seconds() <= 0: return start_dt
  random_seconds = random.randrange(int(delta.total_seconds()))
  return start_dt + timedelta(seconds=random_seconds)

def generate_accidents():
  accident_records = []

  # 30% of eligible rentals
  target_count = int(len(rentals) * 0.3)
  target_rentals = random.sample(rentals, target_count)

  print(f"Generating accident data (Total target rentals: {target_count})...")

  for i, rental in enumerate(target_rentals):
    r_id = rental['rental_id']
    status = rental['status']
    start_date = rental['start_date']

    if status == 'RETURNED':
      end_limit = rental['return_date'] if rental['return_date'] else rental['end_date']
    else:
      end_limit = TODAY.date()

    # 1-3 accidents per rental
    num_accidents = random.randint(1, 3)

    for _ in range(num_accidents):
      acc_dt = generate_random_datetime(start_date, end_limit)
      acc_type = random.choice(ACCIDENT_TYPES)

      # [수정] 한국 도로명 주소 형식 (예: 125 Teheran-ro, Gangnam-gu, Seoul)
      building_no = random.randint(1, 500)
      road = random.choice(ROADS)
      dist = random.choice(DISTRICTS)
      city = random.choice(CITIES)
      acc_loc = f"{building_no} {road}, {dist}, {city}"

      accident_records.append((r_id, acc_dt, acc_type, acc_loc))

    # Batch Insertion
    if len(accident_records) >= BATCH_SIZE:
      insert_accidents(accident_records)
      accident_records = []
      if (i + 1) % 10000 == 0:
        print(f"Progress: {i + 1} / {target_count} rentals processed")

  # Final Insertion
  insert_accidents(accident_records)

def insert_accidents(data):
  if not data: return
  sql = "INSERT INTO ACCIDENT (rental_id, accident_datetime, accident_type, accident_location) VALUES (%s, %s, %s, %s)"
  cursor.executemany(sql, data)
  conn.commit()

try:
  generate_accidents()
  print("ACCIDENT data generation completed!")
except Exception as e:
  print(f"ERROR: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()