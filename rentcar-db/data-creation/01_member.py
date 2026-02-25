import mysql.connector
from datetime import datetime, timedelta
import random
import string

# 1. DB 연결 설정
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
)
cursor = conn.cursor()

TOTAL_COUNT = 500000
BATCH_SIZE = 10000

# [데이터 다양화] 한국 성씨와 이름 구성요소
LAST_NAMES = ['Kim', 'Lee', 'Park', 'Choi', 'Jung', 'Kang', 'Cho', 'Yoon', 'Jang', 'Lim', 'Han', 'Oh', 'Seo', 'Shin', 'Kwon', 'Hwang', 'An', 'Song', 'Ryu', 'Jeon']
FIRST_NAME_CHARS = ['min', 'jun', 'seo', 'yun', 'ji', 'hye', 'woo', 'jin', 'soo', 'ha', 'eun', 'sun', 'young', 'hyun', 'chan', 'jae', 'ho', 'beom', 'ri', 'na']

# [중복 방지] 기존 데이터 로드
used_ids = set()
used_phones = set()
used_emails = set()

cursor.execute("SELECT account_id, phone, email FROM MEMBER")
for row in cursor.fetchall():
  used_ids.add(row[0])
  used_phones.add(row[1])
  used_emails.add(row[2])

def generate_real_name():
  """현실적인 한국인 이름 생성 (예: Kim Min-jun)"""
  last = random.choice(LAST_NAMES)
  # 이름은 보통 두 글자 조합이 많으므로 무작위 조합
  first = random.choice(FIRST_NAME_CHARS) + random.choice(FIRST_NAME_CHARS)
  # 첫 글자 대문자 처리
  return f"{last} {first.capitalize()}"

def generate_unique_account_id():
  chars = string.ascii_letters + string.digits
  while True:
    length = random.randint(8, 15)
    acc_id = ''.join(random.choice(chars) for _ in range(length))
    if acc_id not in used_ids:
      used_ids.add(acc_id)
      return acc_id

def generate_unique_email():
  chars = string.ascii_lowercase + string.digits
  while True:
    length = random.randint(8, 15)
    prefix = ''.join(random.choice(chars) for _ in range(length))
    domain = random.choice(['gmail.com', 'naver.com', 'daum.net', 'kakao.com', 'outlook.com'])
    email = f"{prefix}@{domain}"
    if email not in used_emails:
      used_emails.add(email)
      return email

def generate_unique_phone():
  while True:
    phone = f"010-{random.randint(2000, 9999)}-{random.randint(1000, 9999)}"
    if phone not in used_phones:
      used_phones.add(phone)
      return phone

def generate_account_pw():
  special_chars = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
  length = random.randint(10, 20)
  pw = [
    random.choice(string.ascii_uppercase),
    random.choice(string.ascii_lowercase),
    random.choice(string.digits),
    random.choice(special_chars)
  ]
  all_pool = string.ascii_letters + string.digits + special_chars
  pw += [random.choice(all_pool) for _ in range(length - 4)]
  random.shuffle(pw)
  return ''.join(pw)

def random_date(start_year, end_year):
  start = datetime(start_year, 1, 1)
  end = datetime(end_year, 12, 31)
  delta = end - start
  return (start + timedelta(days=random.randint(0, delta.days))).date()

def generate_records(count):
  records = []
  status_choices = ['ACTIVE']*80 + ['WITHDRAWN']*10 + ['DORMANT']*5 + ['SUSPENDED']*5

  for _ in range(count):
    acc_id = generate_unique_account_id()
    acc_pw = generate_account_pw()
    m_name = generate_real_name()  # [핵심] 실명 생성 함수 호출
    phone = generate_unique_phone()
    email = generate_unique_email()

    join_date = random_date(2020, 2025)
    status = random.choice(status_choices)
    withdraw_date = None

    if status == 'WITHDRAWN':
      today = datetime.today().date()
      days_diff = (today - join_date).days
      withdraw_date = join_date + timedelta(days=random.randint(1, max(1, days_diff)))

    records.append((
      acc_id, acc_pw, m_name, random_date(1960, 2005),
      random.choice(['M', 'F']), phone, email, join_date, withdraw_date, status
    ))
  return records

# 데이터 삽입 실행
try:
  current_total = 0
  while current_total < TOTAL_COUNT:
    data = generate_records(BATCH_SIZE)
    sql = """
            INSERT INTO MEMBER 
            (account_id, account_pw, member_name, birth_date, gender, phone, email, join_date, withdraw_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    cursor.executemany(sql, data)
    conn.commit()
    current_total += BATCH_SIZE
    print(f"{current_total} / {TOTAL_COUNT} records inserted")

except Exception as e:
  print(f"Error: {e}")
  conn.rollback()
finally:
  cursor.close()
  conn.close()

print("MEMBER data generation completed!")