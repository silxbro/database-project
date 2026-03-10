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
cursor.execute("SELECT car_model_id, car_model_type, reg_date, del_date FROM CAR_MODEL")
car_models = cursor.fetchall()

# 3. 보험 유형 및 유형별 가격 비율 (대여료 대비 비율로 산정하면 현실적임)
# FULL: 대여료의 약 20~30%, PART: 약 10~15%, NONE: 0원
insur_types = ['FULL', 'PART', 'NONE']

# 모델 타입별 '기준 보험료' (대략적인 하루치)
base_insur_prices = {
  'COMPACT_MINI': 10000,
  'SMALL': 15000,
  'MEDIUM': 20000,
  'UPPER_MEDIUM': 30000,
  'LARGE': 50000,
  'VAN': 35000,
  'SUV/RV': 25000,
  'EV': 40000
}

def generate_insurance_policies():
  policy_records = []
  today = datetime.now().date()
  one_month_ago = today - timedelta(days=30)
  far_future = datetime.strptime('9999-12-31', '%Y-%m-%d').date()

  for model in car_models:
    m_id = model['car_model_id']
    m_type = model['car_model_type']
    m_reg_date = model['reg_date']
    m_del_date = model['del_date']
    limit_date = m_del_date if m_del_date else far_future

    # 각 보험 유형별로 독립적인 이력을 생성
    for itype in insur_types:
      # 기본 가격 설정
      if itype == 'NONE':
        current_fee = 0
      elif itype == 'PART':
        current_fee = base_insur_prices.get(m_type, 20000) * 0.5
      else: # FULL
        current_fee = base_insur_prices.get(m_type, 20000)

      # 약간의 랜덤 변동성
      current_fee = round(current_fee * random.uniform(0.9, 1.1), -2)

      num_records = random.randint(1, 5)
      current_start = m_reg_date

      for i in range(num_records):
        is_last = (i == num_records - 1)

        # 정책 유지 기간 (1~2년)
        duration = random.randint(365, 730)
        potential_end = current_start + timedelta(days=duration)

        # 종료 조건 판단
        if is_last or potential_end >= one_month_ago or (m_del_date and potential_end >= m_del_date):
          end_date = limit_date
          policy_records.append((m_id, itype, int(current_fee), current_start, end_date))
          break
        else:
          end_date = potential_end
          policy_records.append((m_id, itype, int(current_fee), current_start, end_date))

          # 다음 정책: 보험료는 사고율 등에 따라 오를 수도 있음 (약 2~5% 인상)
          if itype != 'NONE':
            current_fee = round(current_fee * random.uniform(1.02, 1.05), -2)
          current_start = end_date + timedelta(days=1)

  return policy_records

# 4. 데이터 삽입
try:
  policies = generate_insurance_policies()
  print(f"총 {len(policies)}건의 보험료 정책 생성 중...")

  sql = """
        INSERT INTO INSURANCE_FEE_POLICY (car_model_id, insurance_type, fee_amount, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    """

  for i in range(0, len(policies), 1000):
    cursor.executemany(sql, policies[i:i+1000])
    conn.commit()

  print("INSURANCE_FEE_POLICY data generation completed!")

except Exception as e:
  print(f"에러 발생: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()