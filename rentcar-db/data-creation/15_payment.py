import mysql.connector
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

# 1. DB 연결
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
)
cursor = conn.cursor(dictionary=True)

# ---------------------------------------------------------
# [Step 1] 데이터 로딩 및 캐싱 (성능 최적화)
# ---------------------------------------------------------
print("1. Loading policies and metadata into memory...")

# 대여료 정책 캐시
cursor.execute("""
    SELECT p.policy_id, r.car_model_id, r.fee_amount, r.start_date, r.end_date 
    FROM RENTAL_FEE_POLICY r JOIN POLICY p ON p.policy_origin_id = r.policy_id 
    WHERE p.policy_type = 'RENTAL_FEE'
""")
fee_policies = cursor.fetchall()

# 보험료 정책 캐시
cursor.execute("""
    SELECT p.policy_id, i.car_model_id, i.insurance_type, i.fee_amount, i.start_date, i.end_date 
    FROM INSURANCE_FEE_POLICY i JOIN POLICY p ON p.policy_origin_id = i.policy_id 
    WHERE p.policy_type = 'INSURANCE_FEE'
""")
insur_policies = cursor.fetchall()

# 할인 정책 캐시
cursor.execute("""
    SELECT p.policy_id, d.discount_type, d.discount_amount, d.discount_rate, d.start_date, d.end_date 
    FROM DISCOUNT_POLICY d JOIN POLICY p ON p.policy_origin_id = d.policy_id 
    WHERE p.policy_type = 'DISCOUNT'
""")
discount_policies = cursor.fetchall()

# 사고 이력 매핑
cursor.execute("SELECT rental_id, COUNT(*) as cnt FROM ACCIDENT GROUP BY rental_id")
accident_map = {row['rental_id']: row['cnt'] for row in cursor.fetchall()}

# 차량 모델 매핑
cursor.execute("SELECT car_id, car_model_id FROM CAR")
car_model_map = {row['car_id']: row['car_model_id'] for row in cursor.fetchall()}

# ---------------------------------------------------------
# [Step 2] Helper 함수 (Decimal 안전 연산 포함)
# ---------------------------------------------------------
def find_policy(policy_list, model_id, target_date, insur_type=None):
  for p in policy_list:
    if p.get('car_model_id') == model_id:
      if insur_type and p.get('insurance_type') != insur_type:
        continue
      if p['start_date'] <= target_date <= p['end_date']:
        return p
  return None

def find_discount(target_date):
  for d in discount_policies:
    if d['start_date'] <= target_date <= d['end_date']:
      return d
  return None

def get_random_method():
  methods = ['CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER', 'EASY_PAYMENT']
  m = random.choice(methods)

  # 은행 리스트 (English Name 기준)
  banks = ['K-Bank', 'KakaoBank', 'TossBank', 'Shinhan', 'Kookmin', 'Hana', 'Woori', 'NH', 'IBK']
  # 간편 결제 리스트
  easy_pays = ['NaverPay', 'KakaoPay', 'TossPay', 'SamsungPay', 'ApplePay', 'Payco', 'SmilePay']

  if m in ['CREDIT_CARD', 'DEBIT_CARD']:
    # 카드 번호 형식 (16자리)
    m_id = f"{random.randint(4000, 5999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

  elif m == 'BANK_TRANSFER':
    # 은행명 + 계좌번호 형식 (랜덤 조합)
    bank_name = random.choice(banks)
    acc_no = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}"
    m_id = f"{bank_name} {acc_no}"

  elif m == 'EASY_PAYMENT':
    # 간편 결제 브랜드명 + 고유 ID 형식
    pay_name = random.choice(easy_pays)
    # 보통 간편결제는 이메일이나 고유 해시 ID를 사용하므로 섞어서 표현
    if random.random() > 0.5:
      m_id = f"{pay_name}_ID_{random.randint(100000, 999999)}"
    else:
      # 마스킹된 이메일 형식
      m_id = f"{pay_name}(user_{random.randint(100, 999)}***)"

  else:
    m_id = f"UNKNOWN-{random.randint(1000, 9999)}"

  return m, m_id

# ---------------------------------------------------------
# [Step 3] 메인 정산 로직
# ---------------------------------------------------------
print("2. Processing payments (This may take a while)...")
cursor.execute("SELECT * FROM RENTAL")
all_rentals = cursor.fetchall()

detail_batch = []
total_processed = 0

try:
  for rental in all_rentals:
    r_id = rental['rental_id']
    car_id = rental['car_id']
    model_id = car_model_map[car_id]
    res_date = rental['reserve_date']
    status = rental['status']

    # [A] 기본 요금 계산 (RENTAL TYPE)
    days = Decimal(str(max(1, (rental['end_date'] - rental['start_date']).days + 1)))
    fee_p = find_policy(fee_policies, model_id, res_date)
    ins_p = find_policy(insur_policies, model_id, res_date, rental['insurance_type'])
    disc_p = find_discount(res_date)

    unit_fee = Decimal(str(fee_p['fee_amount'] if fee_p else 50000))
    unit_ins = Decimal(str(ins_p['fee_amount'] if ins_p else 0))

    rental_fee_total = unit_fee * days
    insur_fee_total = unit_ins * days

    temp_details = []
    temp_details.append({'type': 'RENTAL_FEE', 'amount': rental_fee_total, 'policy': fee_p['policy_id'] if fee_p else None})
    if insur_fee_total > 0:
      temp_details.append({'type': 'INSURANCE_FEE', 'amount': insur_fee_total, 'policy': ins_p['policy_id'] if ins_p else None})

    # 할인 적용
    discount_amount = Decimal('0')
    if disc_p:
      if disc_p['discount_type'] == 'RATE':
        rate = Decimal(str(disc_p['discount_rate'])) / Decimal('100')
        discount_amount = (rental_fee_total + insur_fee_total) * rate
      else:
        discount_amount = Decimal(str(disc_p['discount_amount']))

      discount_amount = (discount_amount // 10) * 10 # 원단위 절삭
      if discount_amount > 0:
        temp_details.append({'type': 'DISCOUNT_AMOUNT', 'amount': -discount_amount, 'policy': disc_p['policy_id']})

    total_rental_payment = rental_fee_total + insur_fee_total - discount_amount
    p_method, p_m_id = get_random_method()

    # PAYMENT 삽입 (RENTAL)
    pay_dt = datetime.combine(res_date, datetime.min.time()) + timedelta(hours=random.randint(9, 21))
    p_status = 'CANCELED' if status == 'CANCELED' else 'COMPLETED'
    cancel_dt = None
    if p_status == 'CANCELED':
      cancel_dt = datetime.combine(rental['cancel_date'], datetime.min.time()) + timedelta(hours=random.randint(10, 16))

    cursor.execute("""
            INSERT INTO PAYMENT (rental_id, payment_amount, payment_datetime, cancel_datetime, payment_type, payment_method, payment_method_id, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (r_id, total_rental_payment, pay_dt, cancel_dt, 'RENTAL', p_method, p_m_id, p_status))

    new_pay_id = cursor.lastrowid
    for d in temp_details:
      detail_batch.append((new_pay_id, d['policy'], d['amount'], d['type']))

    # [B] 사고 보상금 (COMPENSATION)
    if status == 'RETURNED' and r_id in accident_map and rental['insurance_type'] != 'FULL':
      acc_count = Decimal(str(accident_map[r_id]))
      base_comp = Decimal('200000') if rental['insurance_type'] == 'PART' else Decimal('1000000')
      comp_amount = base_comp * acc_count * Decimal(str(round(random.uniform(0.8, 1.5), 2)))
      comp_amount = (comp_amount // 100) * 100
      comp_dt = datetime.combine(rental['return_date'], datetime.min.time()) + timedelta(minutes=random.randint(60, 180))

      cursor.execute("""
                INSERT INTO PAYMENT (rental_id, payment_amount, payment_datetime, payment_type, payment_method, payment_method_id, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (r_id, comp_amount, comp_dt, 'COMPENSATION', p_method, p_m_id, 'COMPLETED'))

    # [C] 연체료 (ADDITIONAL)
    if status == 'RETURNED' and rental['return_date'] > rental['end_date']:
      over_days = Decimal(str((rental['return_date'] - rental['end_date']).days))
      over_amount = (unit_fee + unit_ins) * over_days
      over_amount = (over_amount // 100) * 100
      add_dt = datetime.combine(rental['return_date'], datetime.min.time()) + timedelta(minutes=15)

      cursor.execute("""
                INSERT INTO PAYMENT (rental_id, payment_amount, payment_datetime, payment_type, payment_method, payment_method_id, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (r_id, over_amount, add_dt, 'ADDITIONAL', p_method, p_m_id, 'COMPLETED'))

    # 상세 내역 배치 삽입
    if len(detail_batch) >= 100000:
      cursor.executemany("""
                INSERT INTO PAYMENT_DETAIL (payment_id, policy_id, payment_detail_amount, payment_detail_type)
                VALUES (%s, %s, %s, %s)
            """, detail_batch)
      detail_batch = []
      conn.commit()
      total_processed += 100000
      print(f"Progress: {total_processed} rentals settled...")

  # 남은 데이터 처리
  if detail_batch:
    cursor.executemany("INSERT INTO PAYMENT_DETAIL (payment_id, policy_id, payment_detail_amount, payment_detail_type) VALUES (%s, %s, %s, %s)", detail_batch)

  conn.commit()
  print("PAYMENT & PAYMENT_DETAIL data generation completed!")

except Exception as e:
  print(f"CRITICAL ERROR: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()