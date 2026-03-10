import mysql.connector
import random  # 내장 라이브러리만 사용
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
  """
  random.gauss를 사용하여 정규분포 값 생성
  mu: 평균, sigma: 표준편차
  """
  mu = (min_val + max_val) / 2
  sigma = (max_val - min_val) / 6

  # 정규분포 값 생성 (범위를 벗어나면 재시도)
  while True:
    val = random.gauss(mu, sigma)
    if min_val <= val <= max_val:
      break

  # step 단위로 반올림
  return int(round(val / step) * step)

def generate_discount_policies():
  policies = []
  current_date = START_TIMELINE

  while current_date < TODAY:
    # 공백 기간 (10~60일)
    gap = random.randint(10, 60)
    current_date += timedelta(days=gap)

    if current_date >= TODAY:
      break

    # 이벤트 기간 (3~20일)
    duration = random.randint(3, 20)
    event_end = current_date + timedelta(days=duration)

    if event_end > TODAY:
      event_end = TODAY

    dist_type = random.choice(['AMOUNT', 'RATE'])
    amount = get_normal_value(5000, 30000, 5000) if dist_type == 'AMOUNT' else None
    rate = get_normal_value(5, 70, 5) if dist_type == 'RATE' else None

    policies.append([dist_type, amount, rate, current_date, event_end])
    current_date = event_end + timedelta(days=1)

  if policies:
    policies[-1][4] = FAR_FUTURE

  return [tuple(p) for p in policies]

# 3. 데이터 삽입
try:
  discount_data = generate_discount_policies()
  print(f"오늘({TODAY})까지의 할인 정책을 생성 중...")

  sql = """
        INSERT INTO DISCOUNT_POLICY 
        (discount_type, discount_amount, discount_rate, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    """

  if discount_data:
    cursor.executemany(sql, discount_data)
    conn.commit()
    last_start = discount_data[-1][3]
    print(f"성공! 총 {len(discount_data)}건 삽입 완료.")
    print(f"마지막 정책 시작일: {last_start}, 종료일: {FAR_FUTURE}")
  else:
    print("생성된 정책 데이터가 없습니다.")

except Exception as e:
  print(f"에러 발생: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()