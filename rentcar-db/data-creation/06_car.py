import mysql.connector
from datetime import datetime, timedelta
import random

# DB 연결 설정
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='ehpark',
    database='rentcar',
)
cursor = conn.cursor(dictionary=True)

TOTAL_COUNT = 5000
BATCH_SIZE = 1000

# -------------------------------
# 1️⃣ 참조 데이터 불러오기
# -------------------------------
cursor.execute("SELECT branch_id FROM BRANCH WHERE status IN ('ACTIVE', 'PAUSED')")
branch_ids = [row['branch_id'] for row in cursor.fetchall()]

cursor.execute("SELECT car_model_id, reg_date, status, del_date FROM CAR_MODEL")
car_models = cursor.fetchall()

if not branch_ids or not car_models:
  raise Exception("❌ BRANCH 또는 CAR_MODEL 테이블에 참조 가능한 데이터가 없습니다!")

# -------------------------------
# 2️⃣ 상태 비율 설정 (10~20% DELETED)
# -------------------------------
deleted_ratio = random.uniform(0.1, 0.2)
status_weights = {
  'ACTIVE': 1 - deleted_ratio,
  'DELETED': deleted_ratio
}
status_list = [status for status, w in status_weights.items() for _ in range(int(w * 100))]

# -------------------------------
# 3️⃣ 랜덤 생성 함수 정의
# -------------------------------
def generate_car_number(i):
  return f"{(i * 97 + random.randint(0, 49)) % 900 + 100:03d}" + \
    chr(65 + (i % 26)) + \
    f"{(i * 7919 + 12345) % 10000:04d}"

def random_year():
  return random.randint(2020, 2025)

def random_mileage():
  return random.randint(10, 100000)

def random_fuel():
  return random.randint(1, 10)

def generate_dates(model, car_year):
  model_reg = datetime.strptime(str(model['reg_date']), "%Y-%m-%d")
  model_status = model['status']
  model_del = datetime.strptime(str(model['del_date']), "%Y-%m-%d") if model['del_date'] else None

  # -------------------------------
  # ✅ ① 등록일(reg_date) 범위 설정
  # -------------------------------
  # 모델 상태에 따른 상한 설정
  if model_status == 'DELETED' and model_del:
    reg_end = model_del
  else:
    reg_end = datetime(2025, 6, 30)

  # 등록일 하한은 모델 등록일과 차량 연식 중 더 늦은 날짜
  car_year_start = datetime(car_year, 1, 1)
  reg_start = max(model_reg, car_year_start)

  if reg_start > reg_end:
    # 비정상 범위 방지 — 최소한 하루 차이 유지
    reg_end = reg_start + timedelta(days=30)

  reg_date = reg_start + timedelta(days=random.randint(0, (reg_end - reg_start).days))

  # -------------------------------
  # ✅ ② 삭제일(del_date) 설정
  # -------------------------------
  del_date = None
  if random.random() < deleted_ratio:  # 약 10~20%만 삭제 처리
    min_del_date = reg_date + timedelta(days=180)
    max_del_date = datetime(2025, 9, 30)
    if min_del_date <= max_del_date:
      del_date = min_del_date + timedelta(days=random.randint(0, (max_del_date - min_del_date).days))

  return reg_date.date(), del_date.date() if del_date else None

# -------------------------------
# 4️⃣ 데이터 생성 함수
# -------------------------------
def generate_records(start_idx, count):
  records = []
  for i in range(start_idx, start_idx + count):
    branch_id = random.choice(branch_ids)
    model = random.choice(car_models)
    car_model_id = model['car_model_id']

    car_year = random_year()
    reg_date, del_date = generate_dates(model, car_year)
    status = 'DELETED' if del_date else 'ACTIVE'

    car_number = generate_car_number(i)
    car_mileage = random_mileage()
    fuel_remaining = random_fuel()

    records.append((
      branch_id, car_model_id, car_number, car_year,
      car_mileage, fuel_remaining, reg_date, del_date, status
    ))
  return records

# -------------------------------
# 5️⃣ 배치 삽입 실행
# -------------------------------
for batch_start in range(1, TOTAL_COUNT + 1, BATCH_SIZE):
  batch_count = min(BATCH_SIZE, TOTAL_COUNT - batch_start + 1)
  data = generate_records(batch_start, batch_count)

  sql = """
        INSERT INTO CAR
        (branch_id, car_model_id, car_number, car_year, car_mileage, fuel_remaining, reg_date, del_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
  cursor.executemany(sql, data)
  conn.commit()
  print(f"{batch_start + batch_count - 1} / {TOTAL_COUNT} records inserted")

cursor.close()
conn.close()
print("CAR data generation completed successfully!")