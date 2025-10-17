DELIMITER $$

DROP PROCEDURE IF EXISTS insert_cars$$

CREATE PROCEDURE insert_cars(IN total_count INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE batch_size INT DEFAULT 10000;

    SET autocommit = 0;
    SET unique_checks = 0;
    SET foreign_key_checks = 0;

    WHILE i <= total_count DO
            SET @sql = 'INSERT INTO CAR (branch_id, car_model_id, car_number, car_year, car_mileage, fuel_remaining, car_status, is_deleted) VALUES ';
            SET @j = 1;

            WHILE @j <= batch_size AND i <= total_count DO
                    SET @branch_id = FLOOR(1 + RAND() * 59);
                    SET @car_model_id = FLOOR(1 + RAND() * 67);

                    SET @car_number = CONCAT(
                            LPAD(MOD(i * 97 + FLOOR(RAND() * 50), 900) + 100, 3, '0'),
                            ELT(MOD(i, 26) + 1,
                                'A','B','C','D','E','F','G','H','I','J','K','L','M',
                                'N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
                            ),
                            LPAD(MOD(i * 7919 + 12345, 10000), 4, '0')
                    );

                    SET @car_year = FLOOR(2020 + RAND() * 6);
                    SET @car_mileage = FLOOR(RAND() * 200000);
                    SET @fuel_remaining = FLOOR(RAND() * 11);
                    SET @car_status = ELT(FLOOR(1 + RAND() * 10), 'AV', 'AV', 'AV', 'AV', 'RS', 'RS', 'RT', 'RT', 'MT', 'RP');
                    SET @is_deleted = IF(RAND() < 0.01, TRUE, FALSE);

                    SET @sql = CONCAT(@sql,
                                      '(', @branch_id, ', "', @car_model_id, '", "', @car_number, '", ',
                                      @car_year, ', ', @car_mileage, ', ', @fuel_remaining, ', "', @car_status, '", ', @is_deleted, ')'
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