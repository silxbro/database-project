import mysql.connector
from datetime import datetime, timedelta
import random

# 1. DB 연결 설정
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
)
cursor = conn.cursor(dictionary=True)

# 2. 상수 설정
TOTAL_COUNT = 5000000
BATCH_SIZE = 100000
TODAY = datetime.now().date()
MIN_DATE = datetime(2020, 1, 1).date()

# 3. 차량 정보 로드
print("실제 차량 정보 로딩 중...")
cursor.execute("SELECT car_id, reg_date, del_date FROM CAR")
car_list = cursor.fetchall()

# 차량별 '예약 행위'가 가능한 시점을 추적 (데이터가 겹치지 않게 순차 생성하기 위함)
car_next_reserve_pos = {}
for car in car_list:
  # 시작점: max(등록일, 2020-01-01)
  car_next_reserve_pos[car['car_id']] = max(car['reg_date'], MIN_DATE)

def generate_records(count):
  records = []

  # 상태 및 보험 비율 설정 (정확한 가중치 적용)
  status_list = ['RESERVED', 'RENTING', 'RETURNED', 'CANCELED']
  status_weights = [20, 10, 60, 10]

  insur_list = ['FULL', 'PART', 'NONE']
  insur_weights = [60, 30, 10]

  for _ in range(count):
    # 1. 차량 선택
    car = random.choice(car_list)
    car_id = car['car_id']
    reg_date = car['reg_date']
    del_date = car['del_date'] if car['del_date'] else TODAY + timedelta(days=365)

    # 2. 상태 결정
    status = random.choices(status_list, weights=status_weights, k=1)[0]

    # 3. 날짜 생성 로직 (철저한 선후 관계 준수)
    # [A] reserve_date 결정 (과거 ~ 오늘 사이에서 고르게 분포)
    current_pos = car_next_reserve_pos[car_id]
    if current_pos > TODAY: # 범위를 넘어가면 다시 해당 차량의 시작점으로 리셋(데이터 순환)
      current_pos = max(reg_date, MIN_DATE)

    reserve_date = current_pos + timedelta(days=random.randint(0, 2)) # 촘촘하게 예약 생성

    # [B] start_date 결정 (reserve_date <= start_date <= reserve_date + 90)
    # reserve_date가 반드시 start_date보다 작거나 같도록 설정
    start_date = reserve_date + timedelta(days=random.randint(0, 90))

    # [C] end_date 결정 (start_date <= end_date <= start_date + 30)
    duration = random.randint(1, 30)
    end_date = start_date + timedelta(days=duration)

    # 변수 초기화
    return_date = None
    return_fuel = None
    cancel_date = None

    # 4. 상태별 날짜 강제 조정 (비즈니스 로직 적용)
    if status == 'RESERVED':
      # 예약: start_date가 오늘보다 뒤여야 함
      if start_date <= TODAY:
        start_date = TODAY + timedelta(days=random.randint(1, 30))
        end_date = start_date + timedelta(days=duration)

    elif status == 'RENTING':
      # 대여중: 오늘이 start_date ~ end_date+3 사이에 걸쳐야 함
      # start_date를 오늘 혹은 오늘 직전으로 강제 조정
      start_date = TODAY - timedelta(days=random.randint(0, duration))
      end_date = start_date + timedelta(days=duration)
      # 만약 조정 후 reserve_date가 start_date보다 커졌다면 reserve_date를 앞으로 당김
      if reserve_date > start_date:
        reserve_date = start_date - timedelta(days=random.randint(0, 7))

    elif status == 'RETURNED':
      # 반납: 70%(정시), 20%(연체), 10%(조기)
      rand_val = random.random()
      if rand_val < 0.7:
        return_date = end_date
      elif rand_val < 0.9:
        return_date = end_date + timedelta(days=random.randint(1, 3))
      else:
        return_date = start_date + timedelta(days=random.randint(0, duration-1))

      # 반납 완료이므로 오늘보다 이전 날짜여야 함
      if return_date >= TODAY:
        diff = (return_date - TODAY).days + 1
        start_date -= timedelta(days=diff)
        end_date -= timedelta(days=diff)
        return_date -= timedelta(days=diff)
        # reserve_date도 같이 당겨서 순서 유지
        if reserve_date > start_date:
          reserve_date = start_date - timedelta(days=random.randint(0, 7))

      return_fuel = random.randint(0, 10)

    elif status == 'CANCELED':
      # 취소: reserve_date <= cancel_date <= min(오늘, start_date-1)
      upper_limit = min(TODAY, start_date - timedelta(days=1))
      if upper_limit < reserve_date: # 모순 발생 시 reserve_date를 당김
        reserve_date = upper_limit - timedelta(days=1)

      days_diff = (upper_limit - reserve_date).days
      cancel_date = reserve_date + timedelta(days=random.randint(0, max(0, days_diff)))

    # 5. 기타 정보
    insurance_type = random.choices(insur_list, weights=insur_weights, k=1)[0]
    start_fuel = random.randint(1, 10)

    # 6. 다음 예약을 위한 시점 업데이트 (중복 방지)
    # 취소가 아닐 경우에만 해당 기간을 점유함
    if status != 'CANCELED':
      final_end = return_date if return_date and return_date > end_date else end_date
      car_next_reserve_pos[car_id] = final_end + timedelta(days=1)
    else:
      # 취소된 경우 해당 차량의 다음 예약은 reserve_date 다음날부터 바로 가능하게 설정
      car_next_reserve_pos[car_id] = reserve_date + timedelta(days=1)

    records.append((
      car_id, start_date, end_date, return_date, insurance_type,
      start_fuel, return_fuel, reserve_date, cancel_date, status
    ))
  return records

# 데이터 삽입 실행 (기존과 동일)
print(f"데이터 생성 및 삽입 시작 (총 {TOTAL_COUNT}건)...")
try:
  for batch_start in range(0, TOTAL_COUNT, BATCH_SIZE):
    data = generate_records(BATCH_SIZE)
    sql = """
            INSERT INTO RENTAL 
            (car_id, start_date, end_date, return_date, insurance_type, start_fuel, return_fuel, reserve_date, cancel_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    cursor.executemany(sql, data)
    conn.commit()
    if (batch_start + BATCH_SIZE) % 100000 == 0:
      print(f"진행 상황: {batch_start + BATCH_SIZE} / {TOTAL_COUNT} 완료")
except Exception as e:
  print(f"에러 발생: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()
  print("RENTAL data generation completed!")