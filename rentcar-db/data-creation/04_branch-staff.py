import random
from datetime import date, timedelta
import string
import mysql.connector

# =========================
# 설정 및 유틸 함수
# =========================
used_staff_numbers = set()
used_phones = set()
used_emails = set()

def random_gender():
  return random.choice(['M', 'F'])

def random_phone():
  while True:
    num = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    if num not in used_phones:
      used_phones.add(num)
      return num

def generate_staff_number(hire_date):
  year_prefix = str(hire_date.year)[2:]
  while True:
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    num = f"{year_prefix}{random_suffix}"
    if num not in used_staff_numbers:
      used_staff_numbers.add(num)
      return num

def random_email(full_name, s_num):
  name_part = full_name.lower().replace(' ', '')
  year_part = s_num[:2]
  email = f"{name_part}{year_part}@dbrentcar.com"

  counter = 1
  original_email = email
  while email in used_emails:
    prefix = original_email.split('@')[0]
    email = f"{prefix}{counter}@dbrentcar.com"
    counter += 1
  used_emails.add(email)
  return email

def random_date(start: date, end: date) -> date:
  delta = (end - start).days
  if delta <= 0: return start
  return start + timedelta(days=random.randint(0, delta))

def random_name():
  surnames = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoon", "Lim", "Han", "Oh"]
  first = ["Ji", "Hyun", "Min", "Soo", "Hye", "Young", "Dong", "Sang", "Seok", "Jae"]
  second = ["Ah", "Bin", "Yeon", "Jin", "Hwa", "Hee", "Kyung", "Sung", "Won", "Na"]
  return random.choice(surnames) + " " + random.choice(first) + random.choice(second)

# =========================
# MySQL 연결
# =========================
conn = mysql.connector.connect(
    host="localhost",
    user="ehpark",
    password="ehPark9463!",
    database="rentcar_db"
)
cur = conn.cursor()

# ACTIVE 지점만 조회
cur.execute("SELECT branch_id FROM BRANCH WHERE status = 'ACTIVE'")
branch_ids = [row[0] for row in cur.fetchall()]

staff_data = []
# 일반 직원 상태 비율 (HEAD 제외용)
normal_status_choices = ['ACTIVE'] * 7 + ['ON_LEAVE'] + ['RETIRED'] * 2

# =========================
# 직원 데이터 생성
# =========================
for branch_id in branch_ids:
  num_staff = random.randint(5, 20)

  # 1. 지점별 직급 리스트 (HEAD 1명 고정)
  positions = ['HEAD'] + ['MANAGER'] * random.randint(1, 3)
  while len(positions) < num_staff:
    positions.append('STAFF')

  for pos in positions:
    name = random_name()
    birth = random_date(date(1980, 1, 1), date(2005, 12, 31))
    hire_start = max(birth.replace(year=birth.year + 20), date(2020, 1, 1))
    hire_date = random_date(hire_start, date.today())
    s_num = generate_staff_number(hire_date)

    # 2. 상태 결정 로직
    if pos == 'HEAD':
      # 활성 지점의 지점장은 무조건 ACTIVE 상태여야 함
      status = 'ACTIVE'
      retire_date = None
    else:
      # 매니저와 일반 스태프는 랜덤 비율 적용
      status = random.choice(normal_status_choices)
      retire_date = None
      if status == 'RETIRED':
        retire_date = random_date(hire_date + timedelta(days=30), date.today())

    staff_data.append({
      'branch_id': branch_id,
      'staff_number': s_num,
      'position': pos,
      'staff_name': name,
      'birth_date': birth,
      'gender': random_gender(),
      'phone': random_phone(),
      'email': random_email(name, s_num),
      'hire_date': hire_date,
      'retire_date': retire_date,
      'status': status
    })

# =========================
# 데이터 삽입
# =========================
sql = """
    INSERT INTO BRANCH_STAFF 
    (branch_id, staff_number, position, staff_name, birth_date, gender, phone, email, hire_date, retire_date, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for s in staff_data:
  cur.execute(sql, (
    s['branch_id'], s['staff_number'], s['position'], s['staff_name'],
    s['birth_date'], s['gender'], s['phone'], s['email'],
    s['hire_date'], s['retire_date'], s['status']
  ))

conn.commit()
cur.close()
conn.close()
print(f"{len(staff_data)} BRANCH_STAFF data generation completed!")