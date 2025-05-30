# RentCar Database

**"RentCar Database"** 는 차량 대여 서비스를 운영하는 기업을 위한 통합 데이터베이스 시스템입니다.
차량, 고객, 대여, 결제 등 핵심 데이터를 구조화하여 관리하고 고성능·고가용성 기반의 서비스를 제공하는 것을 목표로 합니다.

## 1. 프로젝트 개요

### ⭐️ 주요 기능
- 대여 조건 충족 차량 목록 검색
- 차량 상세 조회
- 차량 실시간 대여 가능 여부 확인 및 예약
- 차량 대여 내역 관리: 조회, 변경, 취소
- 차량 대여에 대한 결제
- 지점별 차량 내역 조회: 각 지점의 차량 수, 대여 현황
- 대여/매출 통계 대시보드: 기간 및 지점별 대여 건수, 인기 차종 등 조회

### 🛠️ 기술 스택
- DBMS: Oracle 19c, MySQL 8.0, PostgreSQL
- 데이터 모델링: ERDCloud, SQL Developer, DB Diagram
- 성능 분석: AWR Report, Explain Plan, Autotrace
- 스크립트/자동화: Shell Script, Python
- 운영 환경: AWS RDS, Oracle Cloud

### 📑 요구사항 분석
#### ▶︎ 이해 관계자
- 고객 (개인 및 법인 사용자)
- 차량 대여 서비스 운영 관리자
- 지점 직원
- 관리자

#### ▶︎ 차량 및 지점 관련 요구사항
- 차량은 고유 식별 번호로 관리됩니다.
- 차량은 모델, 연식, 연료 유형, 좌석 수, 주행 거리 등의 기본 정보를 보유합니다.
- 차량은 관련된 대여, 정비, 사고 정보를 기록합니다.
- 차량은 상태 정보(대여 가능, 대여 중, 정비 중)를 유지합니다.
- 차량은 하나의 지점에 소속되며, 각 지점은 여러 대의 차량을 보유 및 관리합니다.
- 차량은 정기 점검 외에도 사고나 고장 발생 시 별도의 정비 이력이 등록됩니다.

#### ▶︎ 차량 대여 관련 요구사항
- 고객은 대여 시작일 24시간 전까지 대여를 예약, 수정 및 취소할 수 있습니다.
- 고객은 대여 목록 및 상세 정보를 확인할 수 있습니다.
- 하나의 대여에서 단일 차량만을 사용할 수 있습니다.
- 하나의 대여에서 여러 운전자를 등록할 수 있으며, 한명의 대표 운전자가 존재합니다.
- 대여 수령/반납 지점은 모두 대여 차량의 관리 지점이어야 합니다.
- 대여는 시작일, 종료일, 대표운전자, 보험/할인 적용 정보 등을 필수적으로 포함하며, 이후 실제 반납 일시, 반납 유류량, 손상/사고 정보, 추가 요금 등의 정보가 추가됩니다.
- 대여 시, 보험상품에 선택적으로 가입할 수 있습니다.
- 계약 조건 위반 시(손상/사고/연체/유류 부족 등) 추가 요금이 자동 계산되어 부과됩니다.

#### ▶︎ 결제/할인 관련 요구사항
- 대여료는 차량, 대여 기간, 보험/할인 적용에 따라 자동 계산됩니다.
- 고객은 대여 신청 시 결제를 진행해야 하며, 결제 완료 시 대여 신청이 최종 확정됩니다.
- 계약 종료 후 추가 요금이 발생할 경우, 별도 결제를 해야 합니다.
- 할인 혜택은 마일리지, 쿠폰, 프로모션 중 한 가지만 적용 가능합니다.
- 마일리지는 차량 반납이 모두 완료된 계약에 한하여 적립됩니다.
- 고객은 보유한 마일리지를 조회하고, 사용하여 대여료를 차감할 수 있습니다.
- 고객은 쿠폰의 유효 기간, 적용 조건에 따라 사용할 수 있습니다.
- 프로모션은 기간 및 조건별로 설정됩니다.
- 관리자는 전체 할인 정책(마일리지, 쿠폰, 프로모션)을 등록, 수정, 삭제할 수 있습니다.

#### ▶︎ 고객/운전자 관련 요구사항
- 고객은 회원ID로 식별할 수 있습니다.
- 고객은 개인 또는 법인일 수 있으며, 법인 고객의 경우 하나의 대표 계약자가 존재합니다.
- 법인 고객은 소속 사용자(운전자)를 복수 등록할 수 있으며, 각 운전자별로 차량을 대여할 수 있습니다.
- 모든 사용자(운전자)는 면허 정보를 등록해야 하며, 유효한 상태여야 차량을 대여할 수 있습니다.

#### ▶︎ 시스템 관리자 관련 요구사항
- 관리자는 전체 고객 계정, 대여 내역, 차량 상태, 정비 이력 등의 데이터를 조회 및 관리할 수 있습니다.
- 관리자는 사용자 유형별 권한(고객, 지점 직원, 관리자 등)을 설정 및 관리할 수 있습니다.
- 관리자는 대여/매출 통계 대시보드를 기반으로 수익, 대여율, 차량 활용률 등을 조회할 수 있습니다.

#### ▶︎ 지점 직원 관련 요구사항
- 지점 직원은 자신이 속한 지점의 차량 목록 및 상태를 조회 및 관리할 수 있습니다.
- 지점 직원은 차량 정비 요청을 등록하거나 완료 처리할 수 있습니다.
- 지점 직원은 고객의 문의사항이나 현장 이슈에 대해 응대 및 처리 로그를 기록할 수 있습니다.


## 2. 데이터베이스 설계
### [1] 개념적 설계

#### ▶︎ 주요 엔티티 및 속성 추출
|엔티티|속성|
|:---|:---|
|**고객** (CUSTOMER)|**고객번호**, 이름, 유형, 휴대전화번호, 이메일|
|**운전자** (DRIVER)|**운전자번호**, **고객번호**, 이름, 생년월일, 면허구분, 면허종류, 면허번호, 발급일, 유효기한|
|**차량** (CAR)|**차량관리번호**, 차량번호, 차량모델, 연료유형, 연식, 주행거리, 좌석수, **관리지점번호**, 상태|
|**지점** (BRANCH)|**지점번호**, 지점명, 주소, 연락처, 영업시작일시, 영업종료일시|
|**대여** (RENTAL)|**대여계약번호**, **대표운전자번호**, **차량관리번호**, 대여일시, 반납예정일시, 반납일시, 보험적용여부,<br/>대여유류량, 반납유류량, 상태|
|**대여운전자** (RENTAL_DRIVER)|**대여계약번호**, **운전자번호**, 순번|
|**결제** (PAYMENT)|**결제번호**, **대여계약번호**, 결제일시, 결제상태, 결제유형, 결제수단, 총결제금액, 대여금액, 보험료,<br/>할인금액, 마일리지사용, 추가결제금액, 보상금|
|**할인이력** (DISCOUNT)|**할인이력번호**, **결제번호**, **할인정책번호**, 할인금액, 할인일시|
|**마일리지이력** (MILEAGE)|**마일리지이력번호**, **마일리지정책번호**, **결제번호**, 이력구분, 적립/사용일시, 적립/사용금액|
|**할인정책** (DISCOUNT_POLICY)|**할인정책번호**, 할인유형, 할인방식, 할인금액/할인율, 시작일, 종료일|
|**마일리지정책** (MILEAGE_POLICY)|**마일리지정책번호**, 적립방식, 적립금액/적립율, 시작일, 종료일|
|**정비이력** (MAINTENANCE)|**정비이력번호**, **차량관리번호**, 정비유형, 시작일자, 완료일자, 비용|
|**수리이력** (REPAIR)|**수리이력번호**, **대여계약번호**, **차량관리번호**, 수리유형, 시작일자, 완료일자, 비용, 처리유형|
|**보상이력** (COMPENSATION)|**보상이력번호**, **차량관리번호**, 보상유형, 비용|
|**사고이력** (ACCIDENT)|**사고이력번호**, **대여계약번호**, **차량관리번호**, 사고일시|

#### ▶︎ 주요 관계 추출
|관계|참여 엔티티 1|참여 엔티티 2|관계 유형|
|:---|:---|:---|:---|
| 고객-운전자 | CUSTOMER (선택) | DRIVER (필수) | 1:N |
| 지점-차량 | BRANCH (필수) | CAR (필수) | 1:N |
| 고객-운전자(직접 연관) | CUSTOMER (선택) | DRIVER (필수) | 1:N |
| 운전자-대여운전자 | DRIVER (선택) | RENTAL_DRIVER (필수) | 1:N |
| 대여-대표운전자 | RENTAL (필수) | DRIVER (필수) | N:1 |
| 대여-차량 | RENTAL (필수) | CAR (필수) | N:1 |
| 대여-대여운전자 | RENTAL (선택) | RENTAL_DRIVER (필수) | 1:N |
| 대여-결제 | RENTAL (선택) | PAYMENT (필수) | 1:N |
| 결제-할인이력 | PAYMENT (선택) | DISCOUNT (선택) | 1:N |
| 결제-마일리지이력 | PAYMENT (선택) | MILEAGE (선택) | 1:N |
| 할인이력-할인정책 | DISCOUNT (필수) | DISCOUNT_POLICY (필수) | N:1 |
| 마일리지이력-마일리지정책 | MILEAGE (필수) | MILEAGE_POLICY (필수) | N:1 |
| 차량-정비이력 | CAR (선택) | MAINTENANCE (필수) | 1:N |
| 차량-수리이력 | CAR (선택) | REPAIR (필수) | 1:N |
| 대여-수리이력 | RENTAL (선택) | REPAIR (선택) | 1:N |
| 차량-보상이력 | CAR (선택) | COMPENSATION (필수) | 1:N |
| 대여-사고이력 | RENTAL (선택) | ACCIDENT (선택) | 1:N |
| 차량-사고이력 | CAR (선택) | ACCIDENT (필수) | 1:N |

#### ▶︎ ERD
<img src="image%2Frentcar_erd.svg" width="750" />

### [2] 논리적 설계
#### [CUSTOMER (고객)]
| 컬럼명     | 컬럼 설명     | 데이터 타입 | 길이 | NULL 여부 | PK  | FK  | 비고             |
|------------|---------------|-------------|------|-----------|-----|-----|------------------|
| customer_id | 고객 ID       | INT         | -    | NOT NULL  | ●   |     | AUTO_INCREMENT   |
| name        | 고객 이름     | VARCHAR     | 50   | NOT NULL  |     |     |                  |
| type        | 고객 유형     | VARCHAR     | 20   | NOT NULL  |     |     | 개인/법인        |
| phone       | 휴대전화번호  | VARCHAR     | 20   | NOT NULL  |     |     | '-' 포함 가능     |
| email       | 이메일        | VARCHAR     | 100  | NULL      |     |     |                  |

#### [CAR (차량)]
| 컬럼명     | 컬럼 설명     | 데이터 타입 | 길이 | NULL 여부 | PK  | FK  | 비고                        |
|------------|---------------|-------------|------|-----------|-----|-----|-----------------------------|
| car_id      | 차량 ID       | INT         | -    | NOT NULL  | ●   |     | AUTO_INCREMENT             |
| car_number  | 차량 번호     | VARCHAR     | 20   | NOT NULL  |     |     | UNIQUE                     |
| model       | 차량 모델     | VARCHAR     | 50   | NOT NULL  |     |     |                             |
| fuel_type   | 연료 유형     | VARCHAR     | 20   | NOT NULL  |     |     |                           |
| year        | 연식         | INT         | -    | NOT NULL  |     |     |                           |
| mileage     | 주행 거리     | INT         | -    | NOT NULL  |     |     | km 단위                    |
| seat_count  | 좌석 수       | INT         | -    | NOT NULL  |     |     |                             |
| branch_id   | 관리 지점 ID  | INT         | -    | NULL      |     | ●   | BRANCH 참조                |
| status      | 차량 상태     | VARCHAR     | 20   | NOT NULL  |     |     |                      |

#### [DRIVER (운전자)]
| 컬럼명         | 컬럼 설명     | 데이터 타입 | 길이 | NULL 여부 | PK  | FK  | 비고                        |
|----------------|---------------|-------------|------|-----------|-----|-----|-----------------------------|
| driver_id       | 운전자 ID     | INT         | -    | NOT NULL  | ●   |     | AUTO_INCREMENT             |
| customer_id     | 고객 ID       | INT         | -    | NULL      |     | ●   | CUSTOMER 참조               |
| name            | 이름          | VARCHAR     | 50   | NOT NULL  |     |     |                             |
| birth_date      | 생년월일      | DATE        | -    | NOT NULL  |     |     | YYYY-MM-DD 형식             |
| license_type    | 면허 구분     | VARCHAR     | 20   | NOT NULL  |     |     | 1종/2종                  |
| license_class   | 면허 종류     | VARCHAR     | 20   | NOT NULL  |     |     | 보통/대형             |
| license_number  | 면허 번호     | VARCHAR     | 50   | NOT NULL  |     |     |                             |
| issue_date      | 발급일        | DATE        | -    | NOT NULL  |     |     |                             |
| expiry_date     | 유효기한      | DATE        | -    | NOT NULL  |     |     |                             |

#### [RENTAL (대여)]
| 컬럼명                 | 컬럼 설명       | 데이터 타입 | 길이 | NULL 여부 | PK  | FK  | 비고                     |
|------------------------|------------------|-------------|------|-----------|-----|-----|--------------------------|
| rental_id              | 계약 ID     | INT         | -    | NOT NULL  | ●   |     | AUTO_INCREMENT          |
| driver_id              | 대표운전자 ID   | INT         | -    | NOT NULL  |     | ●   | DRIVER 참조              |
| car_id                 | 차량 ID          | INT         | -    | NOT NULL  |     | ●   | CAR 참조                 |
| start_datetime         | 대여 시작일시    | DATETIME    | -    | NOT NULL  |     |     |                          |
| expected_return_datetime | 반납 예정일시  | DATETIME    | -    | NOT NULL  |     |     |                          |
| actual_return_datetime | 실제 반납일시    | DATETIME    | -    | NULL      |     |     |                          |
| insurance_yn           | 보험 적용 여부   | BOOLEAN     | -    | NOT NULL  |     |     |                          |
| fuel_start             | 대여시 유류량   | DECIMAL(5,2)| -    | NOT NULL  |     |     |                          |
| fuel_end               | 반납시 유류량   | DECIMAL(5,2)| -    | NULL      |     |     |                          |
| status                 | 대여 상태        | VARCHAR     | 20   | NOT NULL  |     |     |                    |

#### [PAYMENT (결제)]
| 컬럼명            | 컬럼 설명       | 데이터 타입 | 길이 | NULL 여부 | PK  | FK  | 비고               |
|-------------------|------------------|-------------|------|-----------|-----|-----|--------------------|
| payment_id         | 결제 ID          | INT         | -    | NOT NULL  | ●   |     | AUTO_INCREMENT     |
| rental_id          | 대여 계약 ID     | INT         | -    | NOT NULL  |     | ●   | RENTAL 참조        |
| payment_datetime   | 결제 일시        | DATETIME    | -    | NOT NULL  |     |     |                    |
| payment_status     | 결제 상태        | VARCHAR     | 20   | NOT NULL  |     |     |                 |
| payment_type       | 결제 유형        | VARCHAR     | 20   | NOT NULL  |     |     |                  |
| method             | 결제 수단        | VARCHAR     | 20   | NOT NULL  |     |     |                   |
| total_amount       | 총 결제 금액     | INT         | -    | NOT NULL  |     |     |                    |
| rental_amount      | 대여 금액        | INT         | -    | NOT NULL  |     |     |                    |
| insurance_amount   | 보험료           | INT         | -    | NULL      |     |     |                    |
| discount_amount    | 할인 금액        | INT         | -    | NULL      |     |     |                    |
| mileage_used       | 마일리지 사용액  | INT         | -    | NULL      |     |     |                    |
| extra_amount       | 추가 결제 금액   | INT         | -    | NULL      |     |     |                    |
| compensation_amount| 보상금           | INT         | -    | NULL      |     |     |                    |