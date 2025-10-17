import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import random

# MySQL 연결 정보
DB_CONFIG = {
  'host': 'localhost',
  'port': 3306,
  'user': 'root',
  'password': 'ehpark',  # 실제 비밀번호로 변경
  'database': 'rentcar'
}

TOTAL_COUNT = 2000000
BATCH_SIZE = 10000

def random_date(start_date, end_date):
  """start_date와 end_date 사이 랜덤 날짜 반환"""
  delta_days = (end_date - start_date).days
  if delta_days < 0:
    return start_date
  return start_date + timedelta(days=random.randint(0, delta_days))

def generate_rental_record():
  today = date.today()

  customer_id = random.randint(1, 200000)
  car_id = random.randint(1, 10000)
  insurance_type = random.choice(['FULL', 'PART', 'NONE'])
  start_fuel = random.randint(1, 10)

  # 상태 확률
  r = random.random()
  if r < 0.2:
    rental_status = 'RESERVED'
  elif r < 0.3:
    rental_status = 'RENTING'
  elif r < 0.9:
    rental_status = 'RETURNED'
  else:
    rental_status = 'CANCELED'

  # 상태별 날짜 계산
  if rental_status == 'RESERVED':
    start_date = random_date(today + timedelta(days=1), date(2025, 12, 31))
    end_date = random_date(start_date, min(start_date + timedelta(days=30), date(2025, 12, 31)))
    return_date = None
    return_fuel = None

  elif rental_status == 'RENTING':
    start_date = random_date(date(2020,1,1), today)
    end_lo = max((today - timedelta(days=3) - start_date).days, 0)
    end_hi = min(30, (date(2025,12,31) - start_date).days)
    # end_lo > end_hi 보정
    if end_lo > end_hi:
      end_lo = end_hi
    end_offset = random.randint(end_lo, end_hi)
    end_date = start_date + timedelta(days=end_offset)
    return_date = None
    return_fuel = None

  elif rental_status == 'RETURNED':
    start_date = random_date(date(2020,1,1), today)
    end_date = random_date(start_date, min(start_date + timedelta(days=30), date(2025,12,31)))
    end_plus3 = end_date + timedelta(days=3)

    if random.random() < 0.7:
      return_date = end_date
    else:
      return_date = random_date(start_date, min(end_plus3, date(2025,12,31)))

    if return_date > today:
      return_date = today
    return_fuel = random.randint(0, 9)

  else:  # CANCELED
    start_date = random_date(date(2020,1,1), date(2025,12,31))
    end_date = random_date(start_date, min(start_date + timedelta(days=30), date(2025,12,31)))
    return_date = None
    return_fuel = None

  return (customer_id, car_id, start_date, end_date, return_date,
          insurance_type, start_fuel, return_fuel, rental_status)

def insert_rentals(total_count=TOTAL_COUNT, batch_size=BATCH_SIZE):
  try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    conn.autocommit = False

    values = []
    for i in range(1, total_count+1):
      record = generate_rental_record()
      values.append(record)

      if i % batch_size == 0:
        insert_sql = """
                    INSERT INTO RENTAL
                    (customer_id, car_id, start_date, end_date, return_date,
                     insurance_type, start_fuel, return_fuel, rental_status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.executemany(insert_sql, values)
        conn.commit()
        print(f"{i} records inserted...")
        values = []

    # 마지막 배치
    if values:
      insert_sql = """
                INSERT INTO RENTAL
                (customer_id, car_id, start_date, end_date, return_date,
                 insurance_type, start_fuel, return_fuel, rental_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
      cursor.executemany(insert_sql, values)
      conn.commit()
      print(f"Final {len(values)} records inserted.")

  except Error as e:
    print("Error:", e)
    conn.rollback()
  finally:
    cursor.close()
    conn.close()

if __name__ == "__main__":
  insert_rentals()
