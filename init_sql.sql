-- --------------------------------------------------------
-- 主机:                           127.0.0.1
-- 服务器版本:                        10.1.21-MariaDB - mariadb.org binary distribution
-- 服务器操作系统:                      Win32
-- HeidiSQL 版本:                  9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT = @@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0 */;
/*!40101 SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO' */;

-- 导出  表 zeus.class_list_gem 结构
DROP TABLE IF EXISTS `class_list_gem`;
CREATE TABLE IF NOT EXISTS `class_list_gem` (
  `index` BIGINT(20)  DEFAULT NULL,
  `code`  VARCHAR(10) DEFAULT NULL,
  `name`  TEXT,
  KEY `ix_class_list_gem_index` (`index`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.class_list_hs300 结构
DROP TABLE IF EXISTS `class_list_hs300`;
CREATE TABLE IF NOT EXISTS `class_list_hs300` (
  `index`  BIGINT(20)  DEFAULT NULL,
  `code`   VARCHAR(10) DEFAULT NULL,
  `name`   TEXT,
  `date`   TEXT,
  `weight` DOUBLE      DEFAULT NULL,
  KEY `ix_class_list_hs300_index` (`index`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.class_list_sz50 结构
DROP TABLE IF EXISTS `class_list_sz50`;
CREATE TABLE IF NOT EXISTS `class_list_sz50` (
  `index` BIGINT(20)  DEFAULT NULL,
  `code`  VARCHAR(10) DEFAULT NULL,
  `name`  TEXT,
  KEY `ix_class_list_sz50_index` (`index`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.class_list_zz500 结构
DROP TABLE IF EXISTS `class_list_zz500`;
CREATE TABLE IF NOT EXISTS `class_list_zz500` (
  `index`  BIGINT(20)  DEFAULT NULL,
  `code`   VARCHAR(10) DEFAULT NULL,
  `name`   TEXT,
  `date`   TEXT,
  `weight` DOUBLE      DEFAULT NULL,
  KEY `ix_class_list_zz500_index` (`index`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.clmacd_bp 结构
DROP TABLE IF EXISTS `clmacd_bp`;
CREATE TABLE IF NOT EXISTS `clmacd_bp` (
  `id_time` DATETIME    NOT NULL,
  `code`    VARCHAR(50) NOT NULL,
  `price`   DOUBLE      NOT NULL,
  PRIMARY KEY (`id_time`, `code`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.clmacd_result 结构
DROP TABLE IF EXISTS `clmacd_result`;
CREATE TABLE IF NOT EXISTS `clmacd_result` (
  `id_time`  DATETIME NOT NULL,
  `bp_count` INT(11)  NOT NULL,
  `sp_count` INT(11)  NOT NULL,
  PRIMARY KEY (`id_time`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.clmacd_sp 结构
DROP TABLE IF EXISTS `clmacd_sp`;
CREATE TABLE IF NOT EXISTS `clmacd_sp` (
  `id_time` DATETIME    NOT NULL,
  `code`    VARCHAR(50) NOT NULL,
  `price`   DOUBLE      NOT NULL,
  PRIMARY KEY (`id_time`, `code`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.hist_15 结构
DROP TABLE IF EXISTS `hist_15`;
CREATE TABLE IF NOT EXISTS `hist_15` (
  `index`     BIGINT(20)  NOT NULL AUTO_INCREMENT,
  `date`      VARCHAR(20) NOT NULL,
  `open`      DOUBLE               DEFAULT NULL,
  `close`     DOUBLE               DEFAULT NULL,
  `high`      DOUBLE               DEFAULT NULL,
  `low`       DOUBLE               DEFAULT NULL,
  `volume`    DOUBLE               DEFAULT NULL,
  `code`      VARCHAR(20) NOT NULL,
  `ema_short` DOUBLE               DEFAULT NULL,
  `ema_long`  DOUBLE               DEFAULT NULL,
  `dif`       DOUBLE               DEFAULT NULL,
  `dea`       DOUBLE               DEFAULT NULL,
  `macd`      DOUBLE               DEFAULT NULL,
  PRIMARY KEY (`date`, `code`),
  KEY `index` (`index`),
  KEY `date` (`date`)
)
  ENGINE = InnoDB
  AUTO_INCREMENT = 1589768
  DEFAULT CHARSET = utf8
  /*!50100 PARTITION BY KEY (`code`) */;

-- 数据导出被取消选择。
-- 导出  表 zeus.hist_30 结构
DROP TABLE IF EXISTS `hist_30`;
CREATE TABLE IF NOT EXISTS `hist_30` (
  `index`     BIGINT(20)  NOT NULL AUTO_INCREMENT,
  `date`      VARCHAR(20) NOT NULL,
  `open`      DOUBLE               DEFAULT NULL,
  `close`     DOUBLE               DEFAULT NULL,
  `high`      DOUBLE               DEFAULT NULL,
  `low`       DOUBLE               DEFAULT NULL,
  `volume`    DOUBLE               DEFAULT NULL,
  `code`      VARCHAR(20) NOT NULL,
  `ema_short` DOUBLE               DEFAULT NULL,
  `ema_long`  DOUBLE               DEFAULT NULL,
  `dif`       DOUBLE               DEFAULT NULL,
  `dea`       DOUBLE               DEFAULT NULL,
  `macd`      DOUBLE               DEFAULT NULL,
  PRIMARY KEY (`date`, `code`),
  KEY `index` (`index`),
  KEY `macd` (`macd`)
)
  ENGINE = InnoDB
  AUTO_INCREMENT = 1565327
  DEFAULT CHARSET = utf8
  /*!50100 PARTITION BY KEY (`code`) */;

-- 数据导出被取消选择。
-- 导出  表 zeus.his_15 结构
DROP TABLE IF EXISTS `his_15`;
CREATE TABLE IF NOT EXISTS `his_15` (
  `index`     BIGINT(20)  NOT NULL AUTO_INCREMENT,
  `date`      VARCHAR(20) NOT NULL,
  `open`      DOUBLE               DEFAULT NULL,
  `close`     DOUBLE               DEFAULT NULL,
  `high`      DOUBLE               DEFAULT NULL,
  `low`       DOUBLE               DEFAULT NULL,
  `volume`    DOUBLE               DEFAULT NULL,
  `code`      VARCHAR(20) NOT NULL,
  `ema_short` DOUBLE               DEFAULT NULL,
  `ema_long`  DOUBLE               DEFAULT NULL,
  `dif`       DOUBLE               DEFAULT NULL,
  `dea`       DOUBLE               DEFAULT NULL,
  `macd`      DOUBLE               DEFAULT NULL,
  PRIMARY KEY (`date`, `code`),
  KEY `index` (`index`),
  KEY `date` (`date`)
)
  ENGINE = InnoDB
  AUTO_INCREMENT = 655351
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.his_30 结构
DROP TABLE IF EXISTS `his_30`;
CREATE TABLE IF NOT EXISTS `his_30` (
  `index`     BIGINT(20)  NOT NULL AUTO_INCREMENT,
  `date`      VARCHAR(20) NOT NULL,
  `open`      DOUBLE               DEFAULT NULL,
  `close`     DOUBLE               DEFAULT NULL,
  `high`      DOUBLE               DEFAULT NULL,
  `low`       DOUBLE               DEFAULT NULL,
  `volume`    DOUBLE               DEFAULT NULL,
  `code`      VARCHAR(20) NOT NULL,
  `ema_short` DOUBLE               DEFAULT NULL,
  `ema_long`  DOUBLE               DEFAULT NULL,
  `dif`       DOUBLE               DEFAULT NULL,
  `dea`       DOUBLE               DEFAULT NULL,
  `macd`      DOUBLE               DEFAULT NULL,
  PRIMARY KEY (`date`, `code`),
  KEY `index` (`index`),
  KEY `date` (`date`)
)
  ENGINE = InnoDB
  AUTO_INCREMENT = 1638377
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  过程 zeus.move_outdate_data_15 结构
DROP PROCEDURE IF EXISTS `move_outdate_data_15`;
DELIMITER //
CREATE DEFINER =`root`@`localhost` PROCEDURE `move_outdate_data_15`(
  IN `out_date` INT

)
  BEGIN
    SET @num := 0,
    @code := '';

    INSERT IGNORE
    INTO his_15 (`date`,
                 `open`,
                 `close`,
                 high,
                 low,
                 volume,
                 code,
                 ema_short,
                 ema_long,
                 dif,
                 dea,
                 macd)
      SELECT
        `date`,
        `open`,
        `close`,
        high,
        low,
        volume,
        code,
        ema_short,
        ema_long,
        dif,
        dea,
        macd
      FROM (SELECT
              `date`,
              `open`,
              `close`,
              high,
              low,
              volume,
              code,
              ema_short,
              ema_long,
              dif,
              dea,
              macd,
              @num := if(@code = code, @num + 1, 1) AS row_number,
              @code := code                         AS dummy
            FROM hist_15
            ORDER BY code, date DESC) AS x
      WHERE x.row_number > out_date;
    COMMIT;
    DELETE FROM hist_15
    WHERE (`date`, code) IN (SELECT
                               `date`,
                               code
                             FROM his_15);

    COMMIT;
  END//
DELIMITER ;

-- 导出  过程 zeus.move_outdate_data_30 结构
DROP PROCEDURE IF EXISTS `move_outdate_data_30`;
DELIMITER //
CREATE DEFINER =`root`@`localhost` PROCEDURE `move_outdate_data_30`(
  IN `out_date` INT

)
  BEGIN
    SET @num := 0,
    @code := '';

    INSERT IGNORE
    INTO his_30 (`date`,
                 `open`,
                 `close`,
                 high,
                 low,
                 volume,
                 code,
                 ema_short,
                 ema_long,
                 dif,
                 dea,
                 macd)
      SELECT
        `date`,
        `open`,
        `close`,
        high,
        low,
        volume,
        code,
        ema_short,
        ema_long,
        dif,
        dea,
        macd
      FROM (SELECT
              `date`,
              `open`,
              `close`,
              high,
              low,
              volume,
              code,
              ema_short,
              ema_long,
              dif,
              dea,
              macd,
              @num := if(@code = code, @num + 1, 1) AS row_number,
              @code := code                         AS dummy
            FROM hist_30
            ORDER BY code, date DESC) AS x
      WHERE x.row_number > out_date;
    COMMIT;
    DELETE FROM hist_30
    WHERE (`date`, code) IN (SELECT
                               `date`,
                               code
                             FROM his_30);

    COMMIT;
  END//
DELIMITER ;

-- 导出  过程 zeus.run_move_outdate_data 结构
DROP PROCEDURE IF EXISTS `run_move_outdate_data`;
DELIMITER //
CREATE DEFINER =`root`@`localhost` PROCEDURE `run_move_outdate_data`()
  BEGIN
    CALL move_outdate_data_30(40);
    CALL move_outdate_data_15(80);
    COMMIT;
  END//
DELIMITER ;

-- 导出  表 zeus.stock_basics 结构
DROP TABLE IF EXISTS `stock_basics`;
CREATE TABLE IF NOT EXISTS `stock_basics` (
  `code`             VARCHAR(10) DEFAULT NULL,
  `name`             TEXT,
  `industry`         TEXT,
  `area`             TEXT,
  `pe`               DOUBLE      DEFAULT NULL,
  `outstanding`      DOUBLE      DEFAULT NULL,
  `totals`           DOUBLE      DEFAULT NULL,
  `totalAssets`      DOUBLE      DEFAULT NULL,
  `liquidAssets`     DOUBLE      DEFAULT NULL,
  `fixedAssets`      DOUBLE      DEFAULT NULL,
  `reserved`         DOUBLE      DEFAULT NULL,
  `reservedPerShare` DOUBLE      DEFAULT NULL,
  `esp`              DOUBLE      DEFAULT NULL,
  `bvps`             DOUBLE      DEFAULT NULL,
  `pb`               DOUBLE      DEFAULT NULL,
  `timeToMarket`     BIGINT(20)  DEFAULT NULL,
  `undp`             DOUBLE      DEFAULT NULL,
  `perundp`          DOUBLE      DEFAULT NULL,
  `rev`              DOUBLE      DEFAULT NULL,
  `profit`           DOUBLE      DEFAULT NULL,
  `gpr`              DOUBLE      DEFAULT NULL,
  `npr`              DOUBLE      DEFAULT NULL,
  `holders`          BIGINT(20)  DEFAULT NULL,
  KEY `ix_stock_basics_code` (`code`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
-- 导出  表 zeus.time_log 结构
DROP TABLE IF EXISTS `time_log`;
CREATE TABLE IF NOT EXISTS `time_log` (
  `type`             VARCHAR(50) NOT NULL,
  `last_modify_time` DATETIME DEFAULT NULL,
  PRIMARY KEY (`type`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

-- 数据导出被取消选择。
/*!40101 SET SQL_MODE = IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS = IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT = @OLD_CHARACTER_SET_CLIENT */;
