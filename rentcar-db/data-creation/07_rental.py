# rent_generate_rentals_no_overlap.py
import mysql.connector
from datetime import datetime, timedelta
import random
from bisect import bisect_left, insort

# -------------------------
# 설정
# -------------------------
TOTAL_COUNT = 1_000_000   # 생성 목표 (테스트 시 작게 줄이세요)
BATCH_SIZE = 1000         # 배치 커밋 크기 (환경에 맞게 조정)
PER_CAR_MAX = 10          # 한 차량에서 한번에 시도할 최대 생성수 (메모리/속도 밸런스)
REFERENCE_DATE = datetime(2025, 10, 20).date()
MAX_END_LIMIT = datetime(2025, 12, 31).date()

# 상태 비율 (정확한 비율 근사)
STATUS_WEIGHTS = [('RESERVED', 0.20), ('RENTING', 0.10), ('RETURNED', 0.60), ('CANCELED', 0.10)]
STATUS_CHOICES = [s for s, w in STATUS_WEIGHTS for _ in range(int(w*100))]

# 보험 비율
INS_WEIGHTS = [('FULL', 0.6), ('PART', 0.3), ('NONE', 0.1)]
INS_CHOICES = [s for s, w in INS_WEIGHTS for _ in range(int(w*100))]

DB_CONFIG = {
  'host': 'localhost',
  'user': 'root',
  'password': 'ehpark',
  'database': 'rentcar',
  'autocommit': False,
}

# -------------------------
# 유틸 함수
# -------------------------
def choose_status():
  return random.choice(STATUS_CHOICES)

def choose_insurance():
  return random.choice(INS_CHOICES)

def rand_int(a, b):
  return random.randint(a, b)

def date_between(d1, d2):
  """d1 <= random_date <= d2"""
  if d1 > d2:
    return None
  return d1 + timedelta(days=random.randint(0, (d2 - d1).days))

# interval helper: bookings stored as list of (start_date, end_date) sorted by start_date
def is_overlapping_interval(existing, new_start, new_end):
  """
  existing: sorted list of (s,e)
  Check if [new_start, new_end] overlaps or touches any existing interval.
  Requirement: must NOT overlap and must NOT be equal/touch (i.e., new_start <= prev_end or new_end >= next_start are invalid if equality)
  So valid only when prev_end < new_start and new_end < next_start.
  """
  if not existing:
    return False
  i = bisect_left(existing, (new_start, new_end))
  # check previous
  if i > 0:
    prev_s, prev_e = existing[i-1]
    if not (prev_e < new_start):  # prev_e < new_start required (strict)
      return True
  # check next
  if i < len(existing):
    next_s, next_e = existing[i]
    if not (new_end < next_s):   # new_end < next_s required (strict)
      return True
  return False

def insert_booking(existing, new_start, new_end):
  insort(existing, (new_start, new_end))

# -------------------------
# DB에서 ACTIVE CAR 목록 로드
# -------------------------
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor(dictionary=True)

cursor.execute("""
    SELECT car_id, reg_date, del_date
    FROM CAR
    WHERE status = 'ACTIVE'
""")
cars = cursor.fetchall()
if not cars:
  raise SystemExit("ACTIVE 상태인 CAR 데이터가 없습니다.")

# normalize and prepare car info: each has bookings list for non-canceled reservations
car_infos = []
for r in cars:
  car_id = r['car_id']
  reg_date = r['reg_date']
  if isinstance(reg_date, datetime):
    reg_date = reg_date.date()
  del_date = r.get('del_date')
  if isinstance(del_date, datetime):
    del_date = del_date.date()
  max_end = min(del_date, MAX_END_LIMIT) if del_date else MAX_END_LIMIT
  # skip invalid cars where max_end < reg_date
  if reg_date is None:
    reg_date = datetime(2023,1,1).date()
  if max_end < reg_date:
    continue
  car_infos.append({
    'car_id': car_id,
    'reg_date': reg_date,
    'max_end': max_end,
    'bookings': []   # sorted (start,end) for non-canceled rentals
  })

if not car_infos:
  raise SystemExit("사용 가능한 CAR 정보가 없습니다 (reg/del 범위 문제).")

print(f"Loaded {len(car_infos)} active cars.")

# -------------------------
# 레코드 생성기 (비중과 제약을 지키며 겹침 방지)
# -------------------------
def generate_rental_for_car(car):
  """
  한 번 호출 시 car 하나에 대해 최대 PER_CAR_MAX개의 레코드를 생성 시도.
  반환: 리스트 of tuples ready for DB insert (matching RENTAL columns order)
  """
  recs = []
  attempts = 0
  max_attempts = PER_CAR_MAX * 50  # 실패 허용 범위
  while len(recs) < PER_CAR_MAX and attempts < max_attempts:
    attempts += 1
    # 상태, 보험, 연료 등 선택
    status = choose_status()
    insurance = choose_insurance()
    start_fuel = random.randint(1, 10)
    return_fuel = None

    # bounds for start_date:
    earliest_start = car['reg_date']
    latest_start = car['max_end']  # start_date must be <= max_end (we later ensure end_date also <= max_end)

    # pick start_date candidate depending on status constraints
    start_date = None
    end_date = None
    return_date = None
    reserve_date = None
    cancel_date = None

    # ===== status-specific start_date selection =====
    if status == 'RESERVED':
      # start_date > REFERENCE_DATE
      lower = max(earliest_start, REFERENCE_DATE + timedelta(days=1))
      upper = latest_start
      if lower > upper:
        continue
      start_date = date_between(lower, upper)
    elif status == 'RENTING':
      # REFERENCE_DATE must be between start_date and end_date+3
      # So start_date must be in [REFERENCE_DATE - 33 .. REFERENCE_DATE]
      lower = max(earliest_start, REFERENCE_DATE - timedelta(days=33))
      upper = min(latest_start, REFERENCE_DATE)
      if lower > upper:
        continue
      start_date = date_between(lower, upper)
    elif status == 'RETURNED':
      # pick start_date in past/upto REFERENCE_DATE
      lower = earliest_start
      upper = min(latest_start, REFERENCE_DATE)
      if lower > upper:
        continue
      start_date = date_between(lower, upper)
    elif status == 'CANCELED':
      # can be anywhere in available range
      lower = earliest_start
      upper = latest_start
      if lower > upper:
        continue
      start_date = date_between(lower, upper)

    # end_date constraints: start_date <= end_date <= min(start_date+30, max_end)
    max_end_for_start = min(start_date + timedelta(days=30), car['max_end'])
    if start_date > max_end_for_start:
      continue
    end_date = date_between(start_date, max_end_for_start)

    # For non-canceled, need to ensure no overlap with existing car['bookings']
    if status != 'CANCELED':
      # check strict non-overlap (no touching): prev_end < start_date and end_date < next_start
      if is_overlapping_interval(car['bookings'], start_date, end_date):
        # try to adjust: attempt shifting start forward to next possible gap
        # We attempt a few tries by drawing another start between earliest and latest
        shifted_ok = False
        for _ in range(5):
          # try a new start between current end_date+1 and latest_start
          trial_lower = max(car['reg_date'], car['bookings'][-1][1] + timedelta(days=1)) if car['bookings'] else car['reg_date']
          trial_lower = max(trial_lower, start_date)  # don't go earlier than current candidate
          trial_upper = latest_start
          if trial_lower > trial_upper:
            break
          new_start = date_between(trial_lower, trial_upper)
          if new_start is None:
            break
          new_max_end = min(new_start + timedelta(days=30), car['max_end'])
          if new_start > new_max_end:
            continue
          new_end = date_between(new_start, new_max_end)
          if not is_overlapping_interval(car['bookings'], new_start, new_end):
            start_date, end_date = new_start, new_end
            shifted_ok = True
            break
        if not shifted_ok:
          continue

    # ===== reserve_date & cancel_date =====
    # reserve_date in [start_date - 30, start_date - 1]
    r_min = start_date - timedelta(days=30)
    r_max = start_date - timedelta(days=1)
    # allow reserve_date before reg_date if needed, but clamp to reasonable lower bound
    if r_min <= r_max:
      reserve_date = date_between(r_min, r_max)
    else:
      reserve_date = start_date - timedelta(days=1) if start_date - timedelta(days=1) >= car['reg_date'] else None

    if status == 'CANCELED':
      # cancel_date in [reserve_date, start_date - 1]
      if reserve_date:
        cd_min = reserve_date
        cd_max = start_date - timedelta(days=1)
        if cd_min <= cd_max:
          cancel_date = date_between(cd_min, cd_max)
        else:
          cancel_date = cd_min
      else:
        cancel_date = start_date - timedelta(days=1)

    # ===== return_date & return_fuel for RETURNED =====
    if status == 'RETURNED':
      rrand = random.random()
      if rrand < 0.70:
        # 70% exact end_date
        return_date = end_date
      elif rrand < 0.90:
        # 20% end_date < return_date <= end_date+3
        low = end_date + timedelta(days=1)
        high = min(end_date + timedelta(days=3), MAX_END_LIMIT)
        if low > high:
          return_date = end_date
        else:
          return_date = date_between(low, high)
      else:
        # 10% start_date <= return_date < end_date and return_date < REFERENCE_DATE
        if start_date < end_date:
          low = start_date
          high = min(end_date - timedelta(days=1), REFERENCE_DATE - timedelta(days=1))
          if low <= high:
            return_date = date_between(low, high)
          else:
            # fallback
            return_date = end_date
        else:
          return_date = end_date
      return_fuel = random.randint(0, 10)
      # post-check: ensure return_date between start_date and end_date+3
      if not (start_date <= return_date <= end_date + timedelta(days=3)):
        # fix to end_date
        return_date = end_date
        return_fuel = random.randint(0,10)

    # RENTING: ensure REFERENCE_DATE ∈ [start_date, end_date+3]
    if status == 'RENTING':
      if not (start_date <= REFERENCE_DATE <= end_date + timedelta(days=3)):
        continue

    # RESERVED: ensure start_date > REFERENCE_DATE
    if status == 'RESERVED':
      if not (start_date > REFERENCE_DATE):
        continue

    # All constraints satisfied -> append record
    # For DB insert, NULLable fields should be None (py -> mysql connector will map)
    rec_tuple = (
      car['car_id'],
      start_date,
      end_date,
      return_date,
      choose_insurance(),
      start_fuel,
      return_fuel,
      reserve_date,
      cancel_date,
      status
    )

    recs.append(rec_tuple)

    # If non-canceled, register booking interval to prevent overlap
    if status != 'CANCELED':
      insert_booking(car['bookings'], start_date, end_date)

  return recs

# -------------------------
# 메인: 순환 생성 및 배치 삽입
# -------------------------
total_created = 0
batch = []
car_count = len(car_infos)
car_idx = 0

try:
  # 랜덤 시작 포인트로 순환
  random.shuffle(car_infos)
  while total_created < TOTAL_COUNT:
    car = car_infos[car_idx % car_count]
    recs = generate_rental_for_car(car)

    # append to global batch
    for r in recs:
      batch.append(r)
      total_created += 1
      if len(batch) >= BATCH_SIZE:
        insert_sql = """
          INSERT INTO RENTAL
          (car_id, start_date, end_date, return_date, insurance_type, start_fuel, return_fuel, reserve_date, cancel_date, status)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, batch)
        conn.commit()
        print(f"{total_created} / {TOTAL_COUNT} inserted")
        batch = []

        # 10만 건마다 커서 리셋
        if total_created % 50000 == 0 and total_created > 0:
          cursor.close()
          conn.ping(reconnect=True)
          cursor = conn.cursor(dictionary=True)
          print(f"커서 재생성 at {total_created}")

      if total_created >= TOTAL_COUNT:
        break

    car_idx += 1

    # 안전 장치: 만약 충분히 많은 차량을 돌아도 생성량이 정체되면 경고 후 중지
    if car_idx > car_count * 1000 and total_created == 0:
      raise SystemExit("레코드 생성 불가: 제약으로 인해 생성이 전혀 안됩니다.")

  # 마지막 배치 커밋
  if batch:
    insert_sql = """
      INSERT INTO RENTAL
      (car_id, start_date, end_date, return_date, insurance_type, start_fuel, return_fuel, reserve_date, cancel_date, status)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_sql, batch)
    conn.commit()
    print(f"{total_created} / {TOTAL_COUNT} inserted (final batch)")

  print("RENTAL generation completed successfully!")

except Exception as e:
  conn.rollback()
  print("Exception occurred:", e)
  raise
finally:
  cursor.close()
  conn.close()