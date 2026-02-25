import mysql.connector

# 1. DB 연결 설정
conn = mysql.connector.connect(
    host='localhost',
    user='ehpark',
    password='ehPark9463!',
    database='rentcar_db',
)
cursor = conn.cursor()

def sync_policies():
  # 정책 타입과 해당 테이블 및 상세 ID 컬럼 매핑
  # (타입명, 원본 테이블명, 원본 테이블의 PK컬럼명)
  policy_sources = [
    ('RENTAL_FEE', 'RENTAL_FEE_POLICY', 'policy_id'),
    ('INSURANCE_FEE', 'INSURANCE_FEE_POLICY', 'policy_id'),
    ('DISCOUNT', 'DISCOUNT_POLICY', 'policy_id'),
  ]

  total_inserted = 0

  print("통합 운영정책(POLICY) 테이블 데이터 매핑 시작...")

  try:
    # 테이블을 비우고 새로 고침 하려면 아래 주석을 해제하세요.
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    # cursor.execute("TRUNCATE TABLE POLICY;")
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    for p_type, table_name, original_id_col in policy_sources:
      # 1. 원본 테이블에서 상세 ID들 조회
      query = f"SELECT {original_id_col} FROM {table_name}"
      cursor.execute(query)
      rows = cursor.fetchall()

      if not rows:
        print(f" - {p_type}: 매핑할 데이터가 원본 테이블({table_name})에 없습니다.")
        continue

      # 2. POLICY 테이블 형식에 맞게 데이터 준비 (policy_type, policy_origin_id)
      # policy_id는 AUTO_INCREMENT이므로 제외
      insert_data = [(p_type, row[0]) for row in rows]

      # 3. INSERT IGNORE를 사용하여 중복 삽입 방지 (UNIQUE 제약 조건 기준)
      insert_sql = """
                INSERT IGNORE INTO POLICY (policy_type, policy_origin_id) 
                VALUES (%s, %s)
            """
      cursor.executemany(insert_sql, insert_data)

      conn.commit()
      print(f" - {p_type}: {len(insert_data)}건 처리 완료 (신규 삽입: {cursor.rowcount}건)")
      total_inserted += cursor.rowcount

    print(f"\n모든 작업 완료! 현재 POLICY 테이블에 총 {total_inserted}건의 정책 식별자가 등록되었습니다.")

  except Exception as e:
    print(f"에러 발생: {e}")
    conn.rollback()
  finally:
    cursor.close()
    conn.close()

if __name__ == "__main__":
  sync_policies()