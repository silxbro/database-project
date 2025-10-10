DELIMITER $$

DROP PROCEDURE IF EXISTS insert_licenses$$

CREATE PROCEDURE insert_licenses(IN total_count INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE batch_size INT DEFAULT 10000;

    SET autocommit = 0;
    SET unique_checks = 0;
    SET foreign_key_checks = 0;

    WHILE i <= total_count DO
            SET @sql = 'INSERT INTO LICENSE (customer_id, license_number, license_type, license_class, issue_date, expiry_date) VALUES ';
            SET @j = 1;

            WHILE @j <= batch_size AND i <= total_count DO
                    SET @num_str = LPAD(MOD((1103515245 * i + 12345), 1000000), 6, '0');
                    SET @issue_date = DATE_ADD('1975-01-01', INTERVAL FLOOR(RAND() * DATEDIFF(CURDATE(), '1975-01-01')) DAY);
                    SET @license_number = CONCAT(
                            ELT(FLOOR(RAND()*17)+1,
                                '11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','28'
                            ),
                            '-',
                            LPAD(MOD(YEAR(@issue_date), 100), 2, '0'),
                            '-',
                            @num_str,
                            '-',
                            LPAD(FLOOR(RAND()*10), 2, '0')
                    );

                    SET @license_type = ELT(FLOOR(1 + RAND() * 10), 'KO', 'KO', 'KO', 'KO', 'KO', 'KO', 'KO', 'KO', 'KO','IN');
                    SET @license_class = ELT(FLOOR(1 + RAND() * 10), 'L1', 'N1', 'N1', 'N2', 'N2', 'N2', 'N2', 'N2', 'N2', 'A2');
                    SET @expiry_date = STR_TO_DATE(
                            CONCAT(
                                    FLOOR(RAND() * ((YEAR(CURDATE()) + 10) - GREATEST((YEAR(@issue_date) + 10), 2020) + 1) + GREATEST((YEAR(@issue_date) + 10), 2020)),
                                    '-12-31'
                            ),
                            '%Y-%m-%d'
                    );

                    SET @sql = CONCAT(@sql,
                                      '(', i, ', "', @license_number, '", "', @license_type, '", "',
                                      @license_class, '", "', @issue_date, '", "', @expiry_date, '")'
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
