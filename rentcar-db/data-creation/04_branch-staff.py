import random
from datetime import date, timedelta
import string
import pymysql

# =========================
# 설정 및 유틸 함수
# =========================
used_staff_numbers = set()
used_phones = set()
used_emails = set()

def random_gender():
  return random.choice(['M', 'F'])

def random_phone(i):
  while True:
    rand_num = (1103515245 * i + 12345) % 100000000
    num_str = f"{rand_num:08d}"
    phone = f"010-{num_str[:4]}-{num_str[4:]}"
    if phone not in used_phones:
      used_phones.add(phone)
      return phone

def random_staff_number():
  while True:
    num = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    if num not in used_staff_numbers:
      used_staff_numbers.add(num)
      return num

def random_email(name):
  base = name.lower().replace(' ', '.')
  domain = 'company.com'
  email = f"{base}@{domain}"
  counter = 1
  while email in used_emails:
    email = f"{base}{counter}@{domain}"
    counter += 1
  used_emails.add(email)
  return email

def random_date(start: date, end: date) -> date:
  delta = end - start
  if delta.days < 0:
    return start  # start > end인 경우 start 반환
  return start + timedelta(days=random.randint(0, delta.days))

def random_name():
  # 성과 이름 세 글자 구성
  surnames = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoon", "Lim", "Han", "Oh",
              "Seo", "Shin", "Hwang", "Ma", "Jo", "Noh", "Baek", "Hong"]
  first_syllables = ["Ji", "Hyun", "Min", "Soo", "Hye", "Young", "Dong", "Sang", "Seok", "Jae",
                     "Eun", "Ha", "Na", "Woo", "In", "Mi", "Su", "Kyung", "Bin", "Hoon"]
  second_syllables = ["Ah", "Bin", "Yeon", "Jin", "Hwa", "Hee", "Kyung", "Sung", "Won", "Na",
                      "Seo", "Young", "Mi", "Su", "In", "Hye", "Joo", "Ha", "Ri", "Chul"]
  return random.choice(surnames) + " " + random.choice(first_syllables) + random.choice(second_syllables)

# =========================
# 상태, 직책 비율 설정
# =========================
status_choices = ['ACTIVE'] * 7 + ['ON_LEAVE'] + ['RETIRED'] * 2  # 70%/10%/20%
job_titles = ['STAFF', 'MANAGER', 'HEAD']

# =========================
# MySQL 연결 및 운영 지점 조회
# =========================
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='ehpark',
    database='rentcar',
    charset='utf8mb4'
)
cur = conn.cursor()

# 운영 중인 지점만 가져오기 ('PAUSED', 'CLOSED' 제외)
cur.execute("SELECT branch_id FROM BRANCH WHERE status = 'ACTIVE'")
branch_ids = [row[0] for row in cur.fetchall()]
print(f"운영 중인 지점 수: {len(branch_ids)}")

staff_data = []

# =========================
# 직원 데이터 생성
# =========================
for branch_id in branch_ids:
  num_staff = random.randint(3, 15)

  # HEAD 1명
  head_name = random_name()
  birth_date = random_date(date(1980,1,1), date(2005,12,31))
  hire_start = birth_date.replace(year=birth_date.year + 20)
  hire_end = date(2025, 9, 30)
  if hire_start > hire_end:
    hire_start = hire_end
  hire_date = random_date(hire_start, hire_end)

  status = random.choices(status_choices, k=1)[0]
  retire_date = None
  if status == 'RETIRED':
    retire_date = random_date(hire_date, date(2025, 9, 30))

  staff_data.append({
    'branch_id': branch_id,
    'staff_number': random_staff_number(),
    'job_title': 'HEAD',
    'staff_name': head_name,
    'birth_date': birth_date,
    'gender': random_gender(),
    'phone': random_phone(branch_id * 1000 + 0),
    'email': random_email(head_name),
    'hire_date': hire_date,
    'retire_date': retire_date,
    'status': status
  })

  remaining = num_staff - 1
  if remaining <= 0:
    continue

  num_managers = random.randint(1, max(1, remaining//2))
  num_staffs = remaining - num_managers

  for i in range(num_managers):
    name = random_name()
    birth_date = random_date(date(1980,1,1), date(2005,12,31))
    hire_start = birth_date.replace(year=birth_date.year + 20)
    if hire_start > hire_end:
      hire_start = hire_end
    hire_date = random_date(hire_start, hire_end)
    status = random.choices(status_choices, k=1)[0]
    retire_date = None
    if status == 'RETIRED':
      retire_date = random_date(hire_date, date(2025,9,30))
    staff_data.append({
      'branch_id': branch_id,
      'staff_number': random_staff_number(),
      'job_title': 'MANAGER',
      'staff_name': name,
      'birth_date': birth_date,
      'gender': random_gender(),
      'phone': random_phone(branch_id * 1000 + i + 1),
      'email': random_email(name),
      'hire_date': hire_date,
      'retire_date': retire_date,
      'status': status
    })

  for i in range(num_staffs):
    name = random_name()
    birth_date = random_date(date(1980,1,1), date(2005,12,31))
    hire_start = birth_date.replace(year=birth_date.year + 20)
    if hire_start > hire_end:
      hire_start = hire_end
    hire_date = random_date(hire_start, hire_end)
    status = random.choices(status_choices, k=1)[0]
    retire_date = None
    if status == 'RETIRED':
      retire_date = random_date(hire_date, date(2025,9,30))
    staff_data.append({
      'branch_id': branch_id,
      'staff_number': random_staff_number(),
      'job_title': 'STAFF',
      'staff_name': name,
      'birth_date': birth_date,
      'gender': random_gender(),
      'phone': random_phone(branch_id * 1000 + num_managers + i + 1),
      'email': random_email(name),
      'hire_date': hire_date,
      'retire_date': retire_date,
      'status': status
    })

# =========================
# MySQL에 삽입
# =========================
for s in staff_data:
  sql = """
        INSERT INTO BRANCH_STAFF
        (branch_id, staff_number, job_title, staff_name, birth_date, gender, phone, email, hire_date, retire_date, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
  cur.execute(sql, (
    s['branch_id'],
    s['staff_number'],
    s['job_title'],
    s['staff_name'],
    s['birth_date'],
    s['gender'],
    s['phone'],
    s['email'],
    s['hire_date'],
    s['retire_date'],
    s['status']
  ))

conn.commit()
cur.close()
conn.close()

print("BRANCH_STAFF 데이터 삽입 완료")