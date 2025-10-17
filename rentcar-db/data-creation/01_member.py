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
cursor = conn.cursor()

TOTAL_COUNT = 200000
BATCH_SIZE = 10000

# 상태 비율 설정
status_choices = ['ACTIVE']*70 + ['WITHDRAWN']*20 + ['DORMANT']*5 + ['SUSPENDED']*5

# 중복 방지용 세트
used_phones = set()
used_emails = set()

def random_phone(i):
  while True:
    rand_num = (1103515245 * i + 12345) % 100000000
    num_str = f"{rand_num:08d}"
    phone = f"010-{num_str[:4]}-{num_str[4:]}"
    if phone not in used_phones:
      used_phones.add(phone)
      return phone

def random_email(i):
  # 이메일은 인덱스를 이용해 고유하게 생성
  email = f"user{i:08d}@mail.com"
  return email

def random_birth_date():
  start_date = datetime(1955, 1, 1)
  end_date = datetime(2005, 12, 31)
  delta = end_date - start_date
  return (start_date + timedelta(days=random.randint(0, delta.days))).date()

def random_join_date():
  start_date = datetime(2020, 1, 1)
  end_date = datetime(2025, 9, 30)
  delta = end_date - start_date
  return (start_date + timedelta(days=random.randint(0, delta.days))).date()

def random_withdraw_date(join_date):
  # 가입일 이후 ~ 오늘 사이
  today = datetime.today().date()
  delta = today - join_date
  if delta.days <= 0:
    return join_date
  return join_date + timedelta(days=random.randint(1, delta.days))

def random_gender():
  return random.choice(['M', 'F'])

def generate_records(start_idx, count):
  records = []
  for i in range(start_idx, start_idx + count):
    account_id = f"acc{i:08d}"
    account_pw = f"pw{i:08d}"
    member_name = f"user{i:08d}"
    birth_date = random_birth_date()
    gender = random_gender()
    phone = random_phone()
    email = random_email(i)
    join_date = random_join_date()
    status = random.choice(status_choices)
    withdraw_date = random_withdraw_date(join_date) if status == 'WITHDRAWN' else None
    records.append((
      account_id, account_pw, member_name, birth_date, gender, phone, email, join_date, withdraw_date, status
    ))
  return records

# 배치 삽입
for batch_start in range(1, TOTAL_COUNT + 1, BATCH_SIZE):
  batch_count = min(BATCH_SIZE, TOTAL_COUNT - batch_start + 1)
  data = generate_records(batch_start, batch_count)
  sql = """
    INSERT INTO MEMBER
    (account_id, account_pw, member_name, birth_date, gender, phone, email, join_date, withdraw_date, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
  cursor.executemany(sql, data)
  conn.commit()
  print(f"{batch_start + batch_count -1} / {TOTAL_COUNT} records inserted")

cursor.close()
conn.close()
print("Data generation completed!")