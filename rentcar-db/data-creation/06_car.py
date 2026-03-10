import mysql.connector
from datetime import datetime, timedelta
import random

# DB 연결 설정
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
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

# 날짜 객체로 미리 변환 (반복 계산 최적화)
for m in car_models:
  m['parsed_reg_date'] = datetime.strptime(str(m['reg_date']), "%Y-%m-%d")
  m['parsed_del_date'] = datetime.strptime(str(m['del_date']), "%Y-%m-%d") if m['del_date'] else None

if not branch_ids or not car_models:
  raise Exception("❌ BRANCH 또는 CAR_MODEL 테이블에 참조 가능한 데이터가 없습니다!")

deleted_ratio = random.uniform(0.1, 0.2)

# -------------------------------
# 3️⃣ 랜덤 생성 함수 (원본 로직 유지)
# -------------------------------
def generate_car_number(i):
  return f"{(i * 97 + random.randint(0, 49)) % 900 + 100:03d}" + \
    chr(65 + (i % 26)) + \
    f"{(i * 7919 + 12345) % 10000:04d}"

def random_year():
  return random.randint(2020, 2025)

def random_mileage():
  return random.randint(0, 100000)

def random_fuel():
  return random.randint(0, 10)

# -------------------------------
# 4️⃣ 데이터 생성 함수 (균등 분포 로직 적용)
# -------------------------------
def generate_records(start_idx, count):
  records = []

  # 전체 기간 설정
  global_start = datetime(2020, 1, 1)
  global_end = datetime(2025, 12, 31)
  total_days = (global_end - global_start).days

  for i in range(start_idx, start_idx + count):
    # [핵심 1] 등록 날짜(reg_date)를 먼저 전체 기간에서 고르게 뽑음
    reg_date = global_start + timedelta(days=random.randint(0, total_days))

    # [핵심 2] 해당 등록 날짜에 '생산 가능했던' 모델들만 필터링
    available_models = [
      m for m in car_models
      if m['parsed_reg_date'] <= reg_date and (m['parsed_del_date'] is None or m['parsed_del_date'] > reg_date)
    ]

    if not available_models:
      car_model = random.choice(car_models)
      # 방어 코드: 모델 등록일이 선택된 reg_date보다 늦다면 reg_date를 모델 등록일로 조정
      if car_model['parsed_reg_date'] > reg_date:
        reg_date = car_model['parsed_reg_date']
    else:
      car_model = random.choice(available_models)

    car_model_id = car_model['car_model_id']

    # ---------------------------------------------------------
    # ✅ 조건 1: CAR_MODEL.reg_date <= CAR.reg_date < CAR.del_date <= CAR_MODEL.del_date
    # ---------------------------------------------------------
    final_del_date = None
    if random.random() < deleted_ratio:
      # 삭제일 하한선: 등록일 + 180일 (최소 운행 기간)
      min_del_date = reg_date + timedelta(days=180)

      # 삭제일 상한선: 모델의 del_date가 있다면 그 날짜, 없다면 2025-12-31
      limit_del_date = car_model['parsed_del_date'] if car_model['parsed_del_date'] else global_end

      # 만약 상한선이 하한선보다 빠르다면 상한선을 하한선에 맞춤 (데이터 무결성)
      if limit_del_date <= min_del_date:
        final_del_date = limit_del_date
      else:
        days_diff = (limit_del_date - min_del_date).days
        final_del_date = min_del_date + timedelta(days=random.randint(0, days_diff))

    # ---------------------------------------------------------
    # ✅ 조건 2: CAR.car_year = YEAR(reg_date)
    # ---------------------------------------------------------
    car_year = reg_date.year  # YEAR(reg_date) 추출

    branch_id = random.choice(branch_ids)
    status = 'DELETED' if final_del_date else 'ACTIVE'
    car_number = generate_car_number(i)
    car_mileage = random_mileage()
    fuel_remaining = random_fuel()

    records.append((
      branch_id, car_model_id, car_number, car_year,
      car_mileage, fuel_remaining, reg_date.date(),
      final_del_date.date() if final_del_date else None, status
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
print("CAR data generation completed!")