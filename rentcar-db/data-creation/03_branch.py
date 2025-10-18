import mysql.connector
from datetime import date, datetime, timedelta
import random

# MySQL 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ehpark",
    database="rentcar",
)
cursor = conn.cursor()

# BRANCH 데이터 전체
branches = [
  ('Gasan Digital', '3F, 303, 186, Gasan Digital 1-ro, Geumcheon-gu, Seoul', '02-3664-8000', '08:30:00', '18:00:00'),
  ('Gangnam', '1F, 53, Teheran-ro 81-gil, Gangnam-gu, Seoul', '02-3443-8000', '00:00:00', '24:00:00'),
  ('Gongdeok', '2F, Lotte City Hotel, 109, Mapo-daero, Mapo-gu, Seoul', '02-714-8001', '08:30:00', '18:00:00'),
  ('Gwanak', '111, Sinwon Metroville, 1811, Nambusunhwan-ro, Gwanak-gu, Seoul', '02-875-8200', '08:30:00', '18:00:00'),
  ('Guro Digital', '1F, Lotte City Hotel Guro, 300, Digital-ro, Guro-gu, Seoul', '02-866-8003', '08:30:00', '18:00:00'),
  ('Gimpo Airport', '1F, Gate 6, Domestic Terminal, 112, Haneul-gil, Gangseo-gu, Seoul', '02-2663-8000', '08:00:00', '20:00:00'),
  ('Magok', '2F, 210, GMG Tower, 16, Magokjungang 6-ro, Gangseo-gu, Seoul', '02-2659-2009', '08:30:00', '18:00:00'),
  ('Busan Center', '7-7, Jungang-daero 248beon-gil, Dong-gu, Busan', '051-445-9711', '08:30:00', '18:00:00'),
  ('Bucheon Center', '4, Chungseon-ro 203beon-gil, Bupyeong-gu, Incheon', '032-330-9711', '08:30:00', '18:00:00'),
  ('Sangbong', 'C-117, Sangbong Premier’s Emco, 353, Mangu-ro, Jungnang-gu, Seoul', '02-491-8002', '08:30:00', '18:00:00'),
  ('Seoul Station', '1F, 369, Cheongpa-ro, Yongsan-gu, Seoul', '02-715-0010', '00:00:00', '24:00:00'),
  ('Songpa', 'B1-1088, Garden Five Works, 52, Chungmin-ro, Songpa-gu, Seoul', '02-2203-8000', '08:30:00', '18:00:00'),
  ('Suyu', '2F-209, Episode Suyu 838, 315, Dobong-ro, Gangbuk-gu, Seoul', '02-922-8000', '08:30:00', '18:00:00'),
  ('Sindorim', '240, Bldg. 104, Sindorim Prugio 1st, 661, Gyeongin-ro, Guro-gu, Seoul', '02-785-8000', '08:30:00', '18:00:00'),
  ('Yangjae', '206, Yangjae Transfer Parking, 221, Gangnam-daero, Seocho-gu, Seoul', '02-529-8000', '08:30:00', '18:00:00'),
  ('Cheonho', '1F-103, 1065, Cheonho-daero, Gangdong-gu, Seoul', '02-482-8002', '08:30:00', '18:00:00'),
  ('Hongdae', '1F, Cheonghwi Bldg, 176, Donggyo-ro, Mapo-gu, Seoul', '02-2634-8000', '08:30:00', '18:00:00'),
  ('Bucheon', '1F-103, Sewon Bldg, 38, Cheyukgwan-ro, Bupyeong-gu, Incheon', '032-679-8000', '08:30:00', '18:00:00'),
  ('Bundang', '124, 11, Seongnam-daero 925beon-gil, Bundang-gu, Seongnam-si, Gyeonggi-do', '031-701-8007', '08:30:00', '18:00:00'),
  ('Suwon', 'Near Ingye-dong Community Center, 123, Ingye-ro, Paldal-gu, Suwon-si, Gyeonggi-do', '031-215-8181', '08:00:00', '18:00:00'),
  ('Ansan', '108, 57-11, Gojan-ro, Danwon-gu, Ansan-si, Gyeonggi-do', '031-407-8000', '08:00:00', '18:00:00'),
  ('Anyang', '1F-106, 312, Simin-daero, Dongan-gu, Anyang-si, Gyeonggi-do', '031-454-8000', '08:30:00', '18:00:00'),
  ('Osan', '108, 46, Yeokgwangjang-ro, Osan-si, Gyeonggi-do', '031-373-8006', '08:30:00', '18:00:00'),
  ('Incheon', '2F-268, SEE&SEE, 198, Yesul-ro, Namdong-gu, Incheon', '032-881-8000', '08:30:00', '18:00:00'),
  ('Incheon Airport', '1F, Gate 13-14, Terminal 1, 271, Gonghang-ro, Jung-gu, Incheon', '032-743-8000', '08:00:00', '20:00:00'),
  ('Ilsan', '107, 1542, Jungang-ro, Ilsanseo-gu, Goyang-si, Gyeonggi-do', '031-814-8000', '08:30:00', '18:00:00'),
  ('Pyeongtaek', '2F, 26, Seojeongyeok-ro 25beon-gil, Pyeongtaek-si, Gyeonggi-do', '031-667-8000', '08:30:00', '19:00:00'),
  ('Gangneung KTX', '2F, 2, Gangneung-daero 303beon-gil, Gangneung-si, Gangwon-do', '033-645-8002', '08:30:00', '20:00:00'),
  ('Wonju', '114, 50, Mandae Park-gil, Wonju-si, Gangwon-do', '033-764-8000', '08:30:00', '18:00:00'),
  ('Chuncheon', '1F, Suseong Bldg, 7-1, Hyoja-ro, Chuncheon-si, Gangwon-do', '033-243-8000', '08:30:00', '18:00:00'),
  ('Daejeon', '487, Yudeung-ro, Seo-gu, Daejeon', '042-252-8000', '08:00:00', '20:00:00'),
  ('Cheonan Asan KTX', '1F, 210, Gwangjang-ro, Baebang-eup, Asan-si, Chungcheongnam-do', '041-549-0030', '08:30:00', '18:00:00'),
  ('Cheongju', '37, Sajik-daero, Heungdeok-gu, Cheongju-si, Chungcheongbuk-do', '043-213-8000', '08:30:00', '18:00:00'),
  ('Gwangju Airport', '1F, 420-25, Sangmu-daero, Gwangsan-gu, Gwangju', '062-955-8000', '08:30:00', '18:00:00'),
  ('Gwangju Songjeong KTX', '24, Sangmu-daero 205beon-gil, Gwangsan-gu, Gwangju', '062-943-8001', '08:30:00', '18:00:00'),
  ('Gunsan', '14, Haemang-ro, Gunsan-si, Jeollabuk-do', '063-452-8000', '08:30:00', '18:00:00'),
  ('Donggwangju', '1F, Korea Cement Bldg, 239, Mudeung-ro, Buk-gu, Gwangju', '062-412-8000', '08:30:00', '18:00:00'),
  ('Mokpo Station', '100-1, Yeongsan-ro, Mokpo-si, Jeollanam-do', '061-274-8001', '08:30:00', '18:00:00'),
  ('Suncheon KTX', '145, Palma-ro, Suncheon-si, Jeollanam-do', '061-724-8000', '08:30:00', '18:00:00'),
  ('Yeosu EXPO', 'B102, Shinsung Officetel, 90, Deokchungang-gil, Yeosu-si, Jeollanam-do', '061-642-8000', '08:30:00', '18:00:00'),
  ('Yeosu Airport', '386, Yeosun-ro, Yulchon-myeon, Yeosu-si, Jeollanam-do', '061-685-0008', '08:00:00', '17:30:00'),
  ('Iksan KTX', '142, Iksan-daero, Iksan-si, Jeollabuk-do', '063-851-8000', '08:30:00', '18:00:00'),
  ('Jeonju KTX', '675, Dongbu-daero, Deokjin-gu, Jeonju-si, Jeollabuk-do', '063-245-8000', '08:30:00', '18:00:00'),
  ('Gyeongju', '4399-8, Daegyeong-ro, Gyeongju-si, Gyeongsangbuk-do', '054-746-8001', '08:30:00', '18:00:00'),
  ('Gyeongju Station', '80, Singyeongjuyeok-ro, Geoncheon-eup, Gyeongju-si, Gyeongsangbuk-do', '054-746-8001', '08:30:00', '18:00:00'),
  ('Gimcheon Gumi KTX', '1F, 51, Hyeoksin 1-ro, Nam-myeon, Gimcheon-si, Gyeongsangbuk-do', '054-434-8002', '08:30:00', '18:00:00'),
  ('Gimhae Airport', '9, Gonghangap-gil, Gangseo-gu, Busan', '051-941-8000', '08:00:00', '21:00:00'),
  ('Dongdaegu KTX', '1F, 127, Sinamnam-ro, Dong-gu, Daegu', '053-616-8000', '08:00:00', '19:00:00'),
  ('Busan Station', '1F, 7-7, Jungang-daero 248beon-gil, Dong-gu, Busan', '051-442-0091', '08:30:00', '20:00:00'),
  ('Ulsan KTX', '214, 31, Doho-gil, Samnam-eup, Ulju-gun, Ulsan', '052-254-8050', '08:30:00', '18:00:00'),
  ('Ulsan Airport', '1F, 1103, Sanup-ro, Buk-gu, Ulsan', '052-293-8000', '08:00:00', '17:00:00'),
  ('Jinju KTX', '110, 112, Gaeyang-ro, Jinju-si, Gyeongsangnam-do', '055-753-8000', '08:30:00', '17:30:00'),
  ('Changwon Jungang KTX', '101, SH Tower, 18, Yongdong-ro 83beon-an-gil, Uichang-gu, Changwon-si, Gyeongsangnam-do', '055-295-8000', '08:30:00', '18:00:00'),
  ('Pohang KTX', '1F, Pohang Station, 1, Pohangyeok-ro, Heunghaeng-eup, Buk-gu, Pohang-si, Gyeongsangbuk-do', '054-278-8000', '08:30:00', '18:00:00'),
  ('Haeundae', 'B1, La Muette, 620, Haeundae-ro, Haeundae-gu, Busan', '051-744-6160', '08:30:00', '17:30:00'),
  ('Lotte Hotel Jungmun', 'Lotte Hotel Jeju, 35, Jungmungwangwang-ro 72beon-gil, Seogwipo-si, Jeju', '064-738-8101', '09:00:00', '18:00:00'),
  ('Jeju Airport (Jeju Driver Included)', 'Jeju International Airport, 2, Gonghang-ro, Jeju-si, Jeju', '064-751-8000', '06:00:00', '23:00:00'),
  ('Jeju Auto House', '92, Yonghae-ro, Jeju-si, Jeju', '064-751-8000', '06:00:00', '23:00:00'),
]

# 날짜 범위
open_start = date(2020, 1, 1)
open_end = date(2025, 6, 30)
close_end = date(2025, 9, 30)

def random_date(start: date, end: date) -> date:
  delta = end - start
  random_days = random.randint(0, delta.days)
  return start + timedelta(days=random_days)

# 상태 비율
statuses = ["ACTIVE"] * 80 + ["PAUSED"] * 10 + ["CLOSED"] * 10

insert_sql = """
INSERT INTO BRANCH (branch_name, address, phone, open_time, close_time, open_date, close_date, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for name, address, phone, open_t, close_t in branches:
  status = random.choice(statuses)
  open_date = random_date(open_start, open_end)
  close_date = None

  if status == "CLOSED":
    min_close = open_date + timedelta(days=180)
    if min_close > close_end:
      min_close = close_end
    close_date = random_date(min_close, close_end)

  cursor.execute(insert_sql, (name, address, phone, open_t, close_t, open_date, close_date, status))

conn.commit()
cursor.close()
conn.close()

print(f"{len(branches)} rows inserted successfully.")