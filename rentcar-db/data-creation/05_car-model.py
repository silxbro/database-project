import mysql.connector
import random
from datetime import datetime, timedelta

# MySQL 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ehpark",
    database="rentcar",
)
cursor = conn.cursor()

# 날짜 생성 함수
def random_date(start, end):
  delta = end - start
  return start + timedelta(days=random.randint(0, delta.days))

start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 6, 30)
del_end_date = datetime(2025, 9, 30)

# CAR_MODEL 데이터
car_models = [
  ('COMPACT_MINI', 'SPARK', 'Chevrolet', 'GASOLINE', 4),
  ('COMPACT_MINI', 'MORNING', 'Kia', 'GASOLINE', 5),
  ('COMPACT_MINI', 'RAY', 'Kia', 'GASOLINE', 5),
  ('COMPACT_MINI', 'CASPER', 'Hyundai', 'GASOLINE', 4),
  ('SMALL', 'AVANTE', 'Hyundai', 'GASOLINE', 5),
  ('SMALL', 'AVANTE', 'Hyundai', 'HYBRID', 5),
  ('SMALL', 'K3', 'Kia', 'GASOLINE', 5),
  ('MEDIUM', 'K5', 'Kia', 'GASOLINE', 5),
  ('MEDIUM', 'K5', 'Kia', 'HYBRID', 5),
  ('MEDIUM', 'SONATA', 'Hyundai', 'GASOLINE', 5),
  ('MEDIUM', 'SONATA', 'Hyundai', 'HYBRID', 5),
  ('MEDIUM', 'G70', 'Genesis', 'GASOLINE', 5),
  ('UPPER_MEDIUM', 'K8', 'Kia', 'GASOLINE', 5),
  ('UPPER_MEDIUM', 'K8', 'Kia', 'HYBRID', 5),
  ('UPPER_MEDIUM', 'GRANDEUR', 'Hyundai', 'GASOLINE', 5),
  ('UPPER_MEDIUM', 'GRANDEUR', 'Hyundai', 'HYBRID', 5),
  ('LARGE', 'G80', 'Genesis', 'GASOLINE', 5),
  ('LARGE', 'G90', 'Genesis', 'GASOLINE', 5),
  ('LARGE', 'K9', 'Kia', 'GASOLINE', 5),
  ('VAN', 'STARIA', 'Hyundai', 'DIESEL', 9),
  ('VAN', 'STARIA', 'Hyundai', 'DIESEL', 11),
  ('VAN', 'CARNIVAL', 'Kia', 'DIESEL', 9),
  ('VAN', 'CARNIVAL', 'Kia', 'HYBRID', 9),
  ('VAN', 'CARNIVAL HI LIMOUSINE', 'Kia', 'GASOLINE', 7),
  ('VAN', 'CARNIVAL HI LIMOUSINE', 'Kia', 'GASOLINE', 9),
  ('VAN', 'CARNIVAL HI LIMOUSINE', 'Kia', 'HYBRID', 7),
  ('VAN', 'CARNIVAL HI LIMOUSINE', 'Kia', 'HYBRID', 9),
  ('SUV/RV', 'TIVOLI', 'KG Mobility', 'GASOLINE', 5),
  ('SUV/RV', 'TORRES 4WD', 'KG Mobility', 'GASOLINE', 5),
  ('SUV/RV', 'KONA 4WD', 'Hyundai', 'GASOLINE', 5),
  ('SUV/RV', 'NIRO', 'Kia', 'HYBRID', 5),
  ('SUV/RV', 'SELTOS 2WD', 'Kia', 'GASOLINE', 5),
  ('SUV/RV', 'SELTOS 4WD', 'Kia', 'GASOLINE', 5),
  ('SUV/RV', 'SELTOS 4WD', 'Kia', 'DIESEL', 5),
  ('SUV/RV', 'TRAILBLAZER 2WD', 'Chevrolet', 'GASOLINE', 5),
  ('SUV/RV', 'SPORTAGE 2WD', 'Kia', 'GASOLINE', 5),
  ('SUV/RV', 'SPORTAGE 2WD', 'Hyundai', 'HYBRID', 5),
  ('SUV/RV', 'TUCSON 2WD', 'Hyundai', 'GASOLINE', 5),
  ('SUV/RV', 'TUCSON 2WD', 'Hyundai', 'DIESEL', 5),
  ('SUV/RV', 'TUCSON 2WD', 'Hyundai', 'HYBRID', 5),
  ('SUV/RV', 'SANTAFE 2WD', 'Hyundai', 'GASOLINE', 5),
  ('SUV/RV', 'SANTAFE 2WD', 'Hyundai', 'HYBRID', 5),
  ('SUV/RV', 'SANTAFE 4WD', 'Hyundai', 'GASOLINE', 7),
  ('SUV/RV', 'SORENTO 2WD', 'Kia', 'HYBRID', 5),
  ('SUV/RV', 'SORENTO 2WD', 'Kia', 'DIESEL', 5),
  ('SUV/RV', 'SORENTO 4WD', 'Kia', 'DIESEL', 5),
  ('SUV/RV', 'SORENTO 4WD', 'Kia', 'HYBRID', 6),
  ('SUV/RV', 'SORENTO 4WD', 'Kia', 'GASOLINE', 7),
  ('SUV/RV', 'SORENTO 4WD', 'Kia', 'DIESEL', 7),
  ('SUV/RV', 'PALISADE 2WD', 'Hyundai', 'GASOLINE', 7),
  ('SUV/RV', 'PALISADE 2WD', 'Hyundai', 'DIESEL', 7),
  ('SUV/RV', 'PALISADE 2WD', 'Hyundai', 'GASOLINE', 9),
  ('SUV/RV', 'PALISADE 4WD', 'Hyundai', 'GASOLINE', 7),
  ('SUV/RV', 'GV70 2WD', 'Genesis', 'GASOLINE', 5),
  ('SUV/RV', 'GV70 4WD', 'Genesis', 'GASOLINE', 5),
  ('SUV/RV', 'GV80 2WD', 'Genesis', 'GASOLINE', 5),
  ('SUV/RV', 'GV80 4WD', 'Genesis', 'DIESEL', 5),
  ('SUV/RV', 'GV80 4WD', 'Genesis', 'GASOLINE', 7),
  ('SUV/RV', 'GV80 4WD', 'Genesis', 'DIESEL', 7),
  ('EV', 'RAY', 'Kia', 'ELECTRONIC', 5),
  ('EV', 'CASPER', 'Hyundai', 'ELECTRONIC', 4),
  ('EV', 'EV3 2WD', 'Kia', 'ELECTRONIC', 5),
  ('EV', 'EV6 2WD', 'Kia', 'ELECTRONIC', 5),
  ('EV', 'EV9', 'Kia', 'ELECTRONIC', 6),
  ('EV', 'EV9', 'Kia', 'ELECTRONIC', 7),
  ('EV', 'IONIQ5 2WD', 'Hyundai', 'ELECTRONIC', 5),
  ('EV', 'GV70', 'Genesis', 'ELECTRONIC', 5)
]

insert_sql = """
INSERT INTO CAR_MODEL (car_model_type, car_model_base, maker_name, fuel_type, seat_count, reg_date, del_date, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for model in car_models:
  car_model_type, car_model_base, maker_name, fuel_type, seat_count = model

  # 상태 랜덤 부여 (등록 95%, 삭제 5%)
  status = "ACTIVE" if random.random() < 0.95 else "DELETED"

  # 등록일자
  reg_date = random_date(start_date, end_date)

  # 삭제일자
  if status == "DELETED":
    del_start = reg_date + timedelta(days=90)
    if del_start > del_end_date:
      del_start = del_end_date - timedelta(days=30)
    del_date = random_date(del_start, del_end_date)
  else:
    del_date = None

  cursor.execute(insert_sql, (car_model_type, car_model_base, maker_name, fuel_type, seat_count, reg_date.date(), del_date.date() if del_date else None, status))

conn.commit()
cursor.close()
conn.close()

print(f"{len(car_models)} rows inserted successfully.")
