-- 회원 (MEMBER)
CREATE TABLE IF NOT EXISTS MEMBER (
    member_id      INT AUTO_INCREMENT,
    account_id     VARCHAR(20) NOT NULL UNIQUE,
    account_pw     VARCHAR(255) NOT NULL,
    member_name    VARCHAR(20) NOT NULL,
    birth_date     DATE NOT NULL,
    gender         ENUM('M','F') NOT NULL,
    phone          VARCHAR(20) NOT NULL UNIQUE,
    email          VARCHAR(100) NOT NULL UNIQUE,
    join_date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    withdraw_date  DATE NULL,
    status         ENUM('ACTIVE', 'DORMANT', 'SUSPENDED', 'WITHDRAWN') NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (member_id)
);

-- 면허 (DRIVER_LICENSE)
CREATE TABLE IF NOT EXISTS DRIVER_LICENSE (
    license_id      INT AUTO_INCREMENT,
    member_id       INT NOT NULL,
    license_number  VARCHAR(30) NOT NULL UNIQUE,
    license_type    ENUM('DOMESTIC', 'INTERNATIONAL') NOT NULL,
    license_class   ENUM('T1_NORMAL', 'T2_NORMAL', 'T1_LARGE', 'T2_AUTO') NOT NULL,
    issue_date      DATE NOT NULL,
    expiry_date     DATE NOT NULL,
    PRIMARY KEY (license_id)
);

-- 지점 (BRANCH)
CREATE TABLE IF NOT EXISTS BRANCH (
    branch_id    INT AUTO_INCREMENT,
    branch_name  VARCHAR(50) NOT NULL UNIQUE,
    address      VARCHAR(255) NOT NULL,
    phone        VARCHAR(20) NOT NULL UNIQUE,
    open_time    TIME NOT NULL,
    close_time   TIME NOT NULL,
    open_date    DATE NOT NULL,
    close_date   DATE NULL,
    status       ENUM('ACTIVE', 'PAUSED', 'CLOSED') NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (branch_id)
);

-- 지점직원 (BRANCH_STAFF)
CREATE TABLE IF NOT EXISTS BRANCH_STAFF (
    staff_id      INT AUTO_INCREMENT,
    branch_id     INT NOT NULL,
    staff_number  VARCHAR(20) NOT NULL UNIQUE,
    position      ENUM('STAFF', 'MANAGER', 'HEAD') NOT NULL DEFAULT 'STAFF',
    staff_name    VARCHAR(50) NOT NULL,
    birth_date    DATE NOT NULL,
    gender        ENUM('M','F') NOT NULL,
    phone         VARCHAR(20) NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    hire_date     DATE NOT NULL,
    retire_date   DATE NULL,
    status        ENUM('ACTIVE', 'ON_LEAVE', 'RETIRED') NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (staff_id)
);

-- 차량모델 (CAR_MODEL)
CREATE TABLE IF NOT EXISTS CAR_MODEL (
    car_model_id    INT AUTO_INCREMENT,
    car_model_type  ENUM('COMPACT_MINI', 'SMALL', 'MEDIUM', 'UPPER_MEDIUM', 'LARGE', 'VAN', 'SUV/RV', 'EV') NOT NULL,
    car_model_base  VARCHAR(50) NOT NULL,
    maker_name      VARCHAR(50) NOT NULL,
    fuel_type       ENUM('GASOLINE', 'HYBRID', 'DIESEL', 'ELECTRONIC', 'LPG') NOT NULL,
    seat_count      INT NOT NULL,
    reg_date        DATE NOT NULL DEFAULT (CURRENT_DATE),
    del_date        DATE NULL,
    status          ENUM('ACTIVE', 'DELETED') NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (car_model_id),
    UNIQUE KEY (car_model_base, fuel_type, seat_count)
);

-- 차량 (CAR)
CREATE TABLE IF NOT EXISTS CAR (
    car_id          INT AUTO_INCREMENT,
    branch_id       INT NOT NULL,
    car_model_id    INT NOT NULL,
    car_number      VARCHAR(20) NOT NULL UNIQUE,
    car_year        YEAR NOT NULL,
    car_mileage     INT NOT NULL DEFAULT 0,
    fuel_remaining  INT NOT NULL,
    reg_date        DATE NOT NULL,
    del_date        DATE NULL,
    status          ENUM('ACTIVE', 'DELETED') NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (car_id)
);

-- 대여 (RENTAL)
CREATE TABLE IF NOT EXISTS RENTAL (
    rental_id       INT AUTO_INCREMENT,
    car_id          INT NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    return_date     DATE NULL,
    insurance_type  ENUM('FULL', 'PART', 'NONE') NOT NULL,
    start_fuel      INT NOT NULL,
    return_fuel     INT NULL,
    reserve_date    DATE NOT NULL,
    cancel_date     DATE NULL,
    status          ENUM('RESERVED', 'RENTING', 'RETURNED', 'CANCELED') NOT NULL DEFAULT 'RESERVED',
    PRIMARY KEY (rental_id)
);

-- 대여등록운전자 (RENTAL_DRIVER)
CREATE TABLE IF NOT EXISTS RENTAL_DRIVER (
    rental_id   INT NOT NULL,
    driver_id   INT NOT NULL,
    is_primary  BOOLEAN NOT NULL,
    PRIMARY KEY (rental_id, driver_id)
);

-- 결제내역 (PAYMENT)
CREATE TABLE IF NOT EXISTS PAYMENT (
    payment_id         INT AUTO_INCREMENT,
    rental_id          INT NOT NULL,
    payment_amount     DECIMAL(20) NOT NULL,
    payment_datetime   DATETIME NOT NULL DEFAULT NOW(),
    cancel_datetime    DATETIME NULL,
    payment_type       ENUM('RENTAL', 'COMPENSATION', 'ADDITIONAL') NOT NULL,
    ayment_method     ENUM('CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER', 'EASY_PAYMENT') NOT NULL,
    payment_method_id  VARCHAR(50) NOT NULL,
    status             ENUM('COMPLETED', 'CANCELED') NOT NULL DEFAULT 'COMPLETED',
    PRIMARY KEY (payment_id)
);

-- 결제상세내역 (PAYMENT_DETAIL)
CREATE TABLE IF NOT EXISTS PAYMENT_DETAIL (
    payment_detail_id      INT AUTO_INCREMENT,
    payment_id             INT NOT NULL,
    policy_id              INT NOT NULL,
    payment_detail_amount  DECIMAL(20) NOT NULL,
    payment_detail_type    ENUM('RENTAL_FEE', 'INSURANCE_FEE', 'DISCOUNT_AMOUNT') NOT NULL,
    PRIMARY KEY (payment_detail_id)
);

-- 운영정책(POLICY)
CREATE TABLE IF NOT EXISTS POLICY (
    policy_id    INT AUTO_INCREMENT,
    policy_type  ENUM('RENTAL_FEE', 'INSURANCE_FEE', 'DISCOUNT') NOT NULL,
    PRIMARY KEY (policy_id)
);

-- 대여료정책 (RENTAL_FEE_POLICY)
CREATE TABLE IF NOT EXISTS RENTAL_FEE_POLICY (
    policy_id     INT NOT NULL,
    car_model_id  INT NOT NULL,
    fee_amount    DECIMAL(20) NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE NOT NULL,
    PRIMARY KEY (policy_id)
);

-- 보험료정책 (INSURANCE_FEE_POLICY)
CREATE TABLE IF NOT EXISTS INSURANCE_FEE_POLICY (
    policy_id       INT NOT NULL,
    car_model_id    INT NOT NULL,
    insurance_type  ENUM('FULL', 'PART', 'NONE') NOT NULL,
    fee_amount      DECIMAL(20) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    PRIMARY KEY (policy_id)
);

-- 할인정책 (DISCOUNT_POLICY)
CREATE TABLE IF NOT EXISTS DISCOUNT_POLICY (
    policy_id        INT NOT NULL,
    discount_type    ENUM('AMOUNT', 'RATE') NOT NULL,
    discount_amount  DECIMAL(20) NULL,
    discount_rate    INT NULL,
    start_date       DATE NOT NULL,
    end_date         DATE NOT NULL,
    PRIMARY KEY (policy_id)
);

-- 사고이력 (ACCIDENT)
CREATE TABLE IF NOT EXISTS ACCIDENT (
    accident_id        INT AUTO_INCREMENT,
    rental_id          INT NOT NULL,
    accident_datetime  DATETIME NOT NULL,
    accident_type      ENUM('COLLISION', 'SELF_DAMAGE', 'REAR_END', 'SIDE_SWIPE', 'PARKING', 'VIOLATION', 'PEDESTRIAN', 'TIRE/WHEEL') NOT NULL,
    accident_location  VARCHAR(100) NOT NULL,
    PRIMARY KEY (accident_id)
);