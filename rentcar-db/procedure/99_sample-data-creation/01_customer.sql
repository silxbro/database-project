DELIMITER $$

DROP PROCEDURE IF EXISTS insert_customers$$

CREATE PROCEDURE insert_customers(IN total_count INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE batch_size INT DEFAULT 10000;
    DECLARE password_prefix VARCHAR(10) DEFAULT 'pw';
    DECLARE account_prefix VARCHAR(10) DEFAULT 'acc';
    DECLARE name_prefix VARCHAR(10) DEFAULT 'cust';
    DECLARE email_prefix VARCHAR(10) DEFAULT 'myemail';
    DECLARE email_postfix VARCHAR(10) DEFAULT '@mail.com';

    SET autocommit = 0;
    SET unique_checks = 0;
    SET foreign_key_checks = 0;

    WHILE i <= total_count DO
            SET @sql = 'INSERT INTO CUSTOMER (account_id, account_pw, customer_name, birth_date, gender, phone, email, is_deleted) VALUES ';

            SET @j = 1;
            WHILE @j <= batch_size AND i <= total_count DO
                    SET @account_id = CONCAT(account_prefix, LPAD(i, 8, '0'));
                    SET @account_pw = CONCAT(password_prefix, LPAD(i, 8, '0'));
                    SET @customer_name = CONCAT(name_prefix, LPAD(i, 8, '0'));
                    SET @birth_date = DATE_ADD('1955-01-01', INTERVAL FLOOR(RAND() * 18250) DAY);
                    SET @gender = IF(MOD(i, 2) = 0, 'M', 'F');
                    SET @rand_num = MOD((1103515245 * i + 12345), 100000000);
                    SET @num_str = LPAD(@rand_num, 8, '0');
                    SET @phone = CONCAT('010-', SUBSTRING(@num_str, 1, 4), '-', SUBSTRING(@num_str, 5, 4));
                    SET @email = CONCAT(email_prefix, LPAD(i, 8, '0'), email_postfix);
                    SET @is_deleted = IF(MOD(i, 1000) = 0, TRUE, FALSE);

                    SET @sql = CONCAT(@sql,
                                      '("', @account_id, '","', @account_pw, '","', @customer_name, '","', @birth_date, '","', @gender, '","', @phone, '","', @email, '",', @is_deleted, ')'
                               );

                    IF @j < batch_size AND i < total_count THEN
                        SET @sql = CONCAT(@sql, ',');
                    END IF;

                    SET i = i + 1;
                    SET @j = @j + 1;
                END WHILE;

            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        END WHILE;

    SET autocommit = 1;
    SET unique_checks = 1;
    SET foreign_key_checks = 1;
    COMMIT;
END$$

DELIMITER ;