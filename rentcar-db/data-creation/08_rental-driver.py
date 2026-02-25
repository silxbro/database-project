import mysql.connector
import random
from datetime import datetime, timedelta

# 1. DB 연결 설정
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
)
cursor = conn.cursor(dictionary=True)

# 2. 상수 및 기준 날짜 설정
MIN_DATE = datetime(2020, 1, 1).date()
BATCH_SIZE = 50000

# 3. 데이터 로드
print("운전자(MEMBER) 정보 로딩 중...")
# mem_id -> member_id로 수정
cursor.execute("SELECT member_id FROM MEMBER")
all_drivers = [row['member_id'] for row in cursor.fetchall()]

# 운전자별 가용 시작일 관리 (초기값은 시스템 시작일)
driver_next_available = {driver_id: MIN_DATE for driver_id in all_drivers}

print("대여(RENTAL) 정보 로딩 중 (시작일 순 정렬)...")
cursor.execute("""
    SELECT rental_id, start_date, end_date, return_date, status 
    FROM RENTAL 
    ORDER BY start_date ASC
""")
rentals = cursor.fetchall()

def insert_drivers(data):
  if not data:
    return
  sql = "INSERT INTO RENTAL_DRIVER (rental_id, driver_id, is_primary) VALUES (%s, %s, %s)"
  cursor.executemany(sql, data)
  conn.commit()

def generate_rental_drivers():
  driver_assignments = []
  counts_options = [1, 2, 3]
  counts_weights = [40, 40, 20]

  total_rentals = len(rentals)
  print(f"운전자 배정 시작 (총 {total_rentals}건)...")

  for i, rental in enumerate(rentals):
    r_id = rental['rental_id']
    status = rental['status']
    start_date = rental['start_date']
    actual_end = rental['return_date'] if rental['return_date'] else rental['end_date']

    # 1. 운전자 수 결정
    num_drivers = random.choices(counts_options, weights=counts_weights, k=1)[0]

    # 2. 운전자 배정
    # 매번 500만명을 섞는 대신, 무작위로 1000명을 뽑아 그 중 가용한 사람을 찾습니다.
    potential_candidates = random.sample(all_drivers, min(len(all_drivers), 1000))

    assigned_count = 0
    for d_id in potential_candidates:
      if assigned_count >= num_drivers:
        break

      # 스케줄 체크 (취소된 예약은 통과)
      if status == 'CANCELED' or driver_next_available[d_id] <= start_date:
        is_primary = (assigned_count == 0)
        driver_assignments.append((r_id, d_id, is_primary))

        if status != 'CANCELED':
          driver_next_available[d_id] = actual_end + timedelta(days=1)

        assigned_count += 1

    # 3. 만약 가용 운전자가 부족하다면?
    # (비즈니스 로직상 무조건 1명은 있어야 하므로 랜덤하게 한 명 할당)
    if assigned_count == 0:
      emergency_driver = random.choice(all_drivers)
      driver_assignments.append((r_id, emergency_driver, True))

    # 4. 주기적 배치 삽입
    if len(driver_assignments) >= BATCH_SIZE:
      insert_drivers(driver_assignments)
      driver_assignments = []
      print(f"진행 상황: {i+1} / {total_rentals} 완료")

  # 남은 데이터 삽입
  insert_drivers(driver_assignments)

try:
  generate_rental_drivers()
  print("RENTAL_DRIVER data generation completed!")
except Exception as e:
  print(f"ERROR: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()