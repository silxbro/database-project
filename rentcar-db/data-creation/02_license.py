import mysql.connector
from datetime import datetime, timedelta, date
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

# 중복 방지 세트
used_license_numbers = set()

# 확률 기반 선택
def random_license_type():
  return random.choices(['DOMESTIC', 'INTERNATIONAL'], weights=[90, 10])[0]

def random_license_class():
  return random.choices(['T1_NORMAL', 'T2_NORMAL', 'T1_LARGE', 'T2_AUTO'], weights=[30, 50, 10, 10])[0]

# 생년월일을 MEMBER 테이블에서 가져오기
cursor.execute("SELECT member_id, birth_date FROM MEMBER ORDER BY member_id ASC LIMIT %s", (TOTAL_COUNT,))
members = cursor.fetchall()
print(f"{len(members)}명의 MEMBER 데이터를 불러왔습니다.")

# 면허번호 생성 함수
def generate_license_number(issue_date):
  while True:
    prefix = random.choice(['11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','28'])
    year_suffix = str(issue_date.year % 100).zfill(2)
    num_str = str((1103515245 * random.randint(1, 999999) + 12345) % 1000000).zfill(6)
    last_digits = str(random.randint(0, 99)).zfill(2)
    license_number = f"{prefix}-{year_suffix}-{num_str}-{last_digits}"

    if license_number not in used_license_numbers:
      used_license_numbers.add(license_number)
      return license_number

def random_issue_and_expiry(birth_date):
  min_issue = birth_date + timedelta(days=365 * 19)
  max_issue = date(2024, 9, 30)
  if min_issue > max_issue:
    min_issue = max_issue - timedelta(days=365)

  issue_date = min_issue + timedelta(days=random.randint(0, (max_issue - min_issue).days))

  min_expiry = issue_date + timedelta(days=365 * 10)
  max_expiry = date(2035, 12, 31)
  expiry_date = min_expiry + timedelta(days=random.randint(0, (max_expiry - min_expiry).days))

  return issue_date, expiry_date

# 데이터 생성 함수
def generate_license_records(start_idx, members_slice):
  records = []
  for member_id, birth_date in members_slice:
    issue_date, expiry_date = random_issue_and_expiry(birth_date)
    license_number = generate_license_number(issue_date)
    license_type = random_license_type()
    license_class = random_license_class()

    records.append((
      member_id, license_number, license_type, license_class, issue_date, expiry_date
    ))
  return records

# 배치 삽입
for batch_start in range(0, TOTAL_COUNT, BATCH_SIZE):
  batch_end = min(batch_start + BATCH_SIZE, TOTAL_COUNT)
  batch_members = members[batch_start:batch_end]
  data = generate_license_records(batch_start, batch_members)

  sql = """
        INSERT INTO LICENSE
        (member_id, license_number, license_type, license_class, issue_date, expiry_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
  cursor.executemany(sql, data)
  conn.commit()
  print(f"{batch_end} / {TOTAL_COUNT} records inserted")

cursor.close()
conn.close()
print("LICENSE data generation completed!")
