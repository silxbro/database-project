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
    # 즉, 모델의 등록일 <= 차량의 등록일 && (모델 삭제일이 없거나 >= 차량의 등록일)
    available_models = [
      m for m in car_models
      if m['parsed_reg_date'] <= reg_date and (m['parsed_del_date'] is None or m['parsed_del_date'] >= reg_date)
    ]

    # 만약 해당 날짜에 가능한 모델이 하나도 없다면 전체 모델 중 하나 선택 (방어 코드)
    if not available_models:
      car_model = random.choice(car_models)
    else:
      car_model = random.choice(available_models)

    car_model_id = car_model['car_model_id']

    # [핵심 3] 삭제일(del_date) 설정 (원본 제약 유지)
    final_del_date = None
    if random.random() < deleted_ratio:
      min_del_date = reg_date + timedelta(days=180)
      if min_del_date <= global_end:
        days_diff = (global_end - min_del_date).days
        final_del_date = min_del_date + timedelta(days=random.randint(0, days_diff))

    branch_id = random.choice(branch_ids)
    car_year = random_year()
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