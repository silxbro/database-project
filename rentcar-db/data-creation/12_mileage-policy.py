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

# 2. 기준 설정
START_TIMELINE = datetime(2020, 1, 1).date()
TODAY = datetime.now().date()
FAR_FUTURE = datetime.strptime('9999-12-31', '%Y-%m-%d').date()

def get_normal_value(min_val, max_val, step):
  """중앙값이 많이 나오는 정규분포 값 생성 (step 단위)"""
  mu = (min_val + max_val) / 2
  sigma = (max_val - min_val) / 6

  while True:
    val = random.gauss(mu, sigma)
    if min_val <= val <= max_val:
      break

  return int(round(val / step) * step)

def generate_mileage_policies():
  policies = []
  current_date = START_TIMELINE

  while current_date < TODAY:
    # 정책 간의 공백 (마일리지는 상시 혜택인 경우가 많으므로 할인보다 공백을 짧게 설정)
    gap = random.randint(5, 30)
    current_date += timedelta(days=gap)

    if current_date >= TODAY:
      break

    # 마일리지 이벤트/정책 유지 기간 (15일 ~ 60일)
    duration = random.randint(15, 60)
    event_end = current_date + timedelta(days=duration)

    if event_end > TODAY:
      event_end = TODAY

    # 적립 방식 결정
    earn_type = random.choice(['AMOUNT', 'RATE'])
    amount = None
    rate = None

    if earn_type == 'AMOUNT':
      # 1,000 ~ 10,000 (1,000 단위)
      amount = get_normal_value(1000, 10000, 1000)
    else:
      # 5% ~ 30% (5% 단위)
      rate = get_normal_value(5, 30, 5)

    policies.append([earn_type, amount, rate, current_date, event_end])
    current_date = event_end + timedelta(days=1)

  # 마지막 레코드 종료일 9999-12-31로 연장
  if policies:
    policies[-1][4] = FAR_FUTURE

  return [tuple(p) for p in policies]

# 3. 데이터 삽입
try:
  mileage_data = generate_mileage_policies()
  print(f"마일리지 적립 정책을 생성 중 (기준일: {TODAY})...")

  sql = """
        INSERT INTO MILEAGE_POLICY 
        (earning_type, earning_amount, earning_rate, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    """

  if mileage_data:
    cursor.executemany(sql, mileage_data)
    conn.commit()
    print(f"성공! 총 {len(mileage_data)}건 삽입 완료.")
    print(f"최신 정책 종료일이 {FAR_FUTURE}로 설정되었습니다.")
  else:
    print("생성된 데이터가 없습니다.")

except Exception as e:
  print(f"에러 발생: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()