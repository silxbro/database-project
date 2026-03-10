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

# 2. 기준 정보 로드
print("차량 모델 정보 로딩 중...")
cursor.execute("SELECT car_model_id, car_model_base, car_model_type, reg_date, del_date FROM CAR_MODEL")
car_models = cursor.fetchall()

# 3. 모델 타입별 기본 가격 설정 (현실성 반영)
base_prices = {
  'COMPACT_MINI': 40000,    # 캐스퍼, 모닝 등
  'SMALL': 60000,           # 아반떼, K3 등
  'MEDIUM': 90000,          # 소나타, K5 등
  'UPPER_MEDIUM': 120000,   # 그랜저, K8 등
  'LARGE': 180000,          # 제네시스 G90, 에쿠스 등
  'VAN': 130000,            # 스타리아, 카니발 등
  'SUV/RV': 110000,         # 싼타페, 쏘렌토 등
  'EV': 150000              # 아이오닉, 테슬라 등
}

def generate_fee_policies():
  policy_records = []
  today = datetime.now().date()
  one_month_ago = today - timedelta(days=30)
  far_future = datetime.strptime('9999-12-31', '%Y-%m-%d').date()

  for car_model in car_models:
    m_id = car_model['car_model_id']
    m_type = car_model['car_model_type']
    m_reg_date = car_model['reg_date']
    m_del_date = car_model['del_date']

    # 모델별 기본가에서 약간의 변동성 추가 (±10%)
    current_fee = base_prices.get(m_type, 100000) * random.uniform(0.9, 1.1)
    current_fee = round(current_fee, -2)  # 100원 단위 절삭

    # 1~5개의 레코드 생성
    num_records = random.randint(1, 5)

    # 첫 시작일은 모델 등록일
    current_start = m_reg_date

    # 모델 삭제일이 있다면 정책 종료의 한계선 설정
    limit_date = m_del_date if m_del_date else far_future

    for i in range(num_records):
      is_last = (i == num_records - 1)

      # 다음 시작일 계산 (대략 1년~2년 사이 정책 변경)
      # 단, '한 달 전'보다는 미래로 가지 않도록 조정 (최신 이력이 9999년까지 가야 하므로)
      duration = random.randint(365, 730)
      potential_end = current_start + timedelta(days=duration)

      # 조건 체크:
      # 1. 마지막 레코드이거나
      # 2. 다음 종료일이 '한 달 전' 혹은 '모델 삭제일'을 넘어가는 경우 강제 종료
      if is_last or potential_end >= one_month_ago or (m_del_date and potential_end >= m_del_date):
        end_date = limit_date
        policy_records.append((m_id, int(current_fee), current_start, end_date))
        break
      else:
        end_date = potential_end
        policy_records.append((m_id, int(current_fee), current_start, end_date))

        # 다음 정책 준비: 가격 인상 및 시작일 갱신
        current_fee *= random.uniform(1.03, 1.08)  # 3~8% 인상
        current_fee = round(current_fee, -2)
        current_start = end_date + timedelta(days=1)

  return policy_records

# 4. 데이터 삽입
try:
  policies = generate_fee_policies()
  print(f"총 {len(policies)}건의 정책 생성 중...")

  sql = """
        INSERT INTO RENTAL_FEE_POLICY (car_model_id, fee_amount, start_date, end_date)
        VALUES (%s, %s, %s, %s)
    """

  # 1000건씩 분할 삽입
  for i in range(0, len(policies), 1000):
    cursor.executemany(sql, policies[i:i+1000])
    conn.commit()

  print("RENTAL_FEE_POLICY data generation completed!")

except Exception as e:
  print(f"에러 발생: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()