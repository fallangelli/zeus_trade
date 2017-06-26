# coding:utf-8
import logging
from datetime import datetime, timedelta

import configparser
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base_model import TimeLog, StockBasic, ClmacdBp, ClmacdSp, ClmacdResult

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


class BaseDB:
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        username = cf.get('db_conf', 'username')
        password = cf.get('db_conf', 'password')
        server = cf.get('db_conf', 'server')
        database = cf.get('db_conf', 'database')

        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')

        self.__engine = create_engine(
            'mysql+pymysql://' + username + ':' + password + '@' + server + '/' + database + '?charset=utf8',
            pool_size=1024, pool_recycle=300)

    def get_engine(self):
        return self.__engine

    def update_log_time(self, log_type):
        engine = self.__engine
        session = sessionmaker(bind=engine)()
        time_log = TimeLog(type=log_type, last_modify_time=datetime.now())
        session.merge(time_log)
        session.commit()
        session.close()

    def get_all_stock_list(self):
        session = sessionmaker(bind=self.__engine)()
        ret_list = session.query(StockBasic)
        session.close()
        return ret_list

    def get_all_macd_data(self, k_type):
        table_name = 'hist_' + k_type
        data = pd.read_sql_table(table_name, self.get_engine(),
                                 columns=['code', 'date', 'close', 'ema_short', 'ema_long', 'dif', 'dea', 'macd'])
        return data

    def get_macd_data(self, code, k_type):
        table_name = 'hist_' + k_type
        data = pd.read_sql_query(
            "SELECT code,`date`,close,ema_short,ema_long,dif,dea,macd FROM  " + table_name + " WHERE  code='" + code + "'",
            con=self.__engine)
        return data

    def get_max_macd(self, code):
        sql = "select min(c.md) from (\
                 select max(`date`) md from hist_30 where code = '%s'\
                 union\
                 select max(`date`) md from hist_15 where code = '%s'\
                 ) c" % (code, code)
        max_date = pd.read_sql_query(sql, con=self.__engine)
        return max_date.values[0][0]

    def get_need_to_refresh_list(self):
        session = sessionmaker(bind=self.__engine)()
        query = session.query(TimeLog)
        session.close()
        last_fetch_time = query.filter(TimeLog.id == 1).first().last_modify_time
        print('last_fetch_time:', last_fetch_time)
        if (datetime.now() - last_fetch_time).days > 1:
            return True
        return False

    def get_data_need_to_macd(self, k_type):
        table_name = 'hist_' + k_type
        ret_data = pd.read_sql_query("SELECT * FROM (\
                                        SELECT code,date,close,ema_short,ema_long,dif,dea,macd FROM " + table_name + " \
                                        WHERE (date,code) IN (SELECT max(date) md,code cd FROM " + table_name + " \
                                        WHERE macd IS NOT NULL GROUP BY code)\
                                        UNION\
                                        SELECT code,date,close,ema_short,ema_long,dif,dea,macd FROM " + table_name + " \
                                        WHERE macd IS NULL) c ORDER BY c.code, c.date", con=self.__engine)
        return ret_data

    def get_all_date_list(self, k_type):
        table_name = 'hist_' + k_type
        ret_val = pd.read_sql_query('SELECT code,date FROM ' + table_name, con=self.__engine)
        return ret_val

    def get_date_list(self, code, k_type):
        table_name = 'hist_' + k_type
        ret_val = pd.read_sql_query("SELECT code,date FROM " + table_name + " where code = '" + code + "'",
                                    con=self.__engine)
        return ret_val

    def get_macd_data(self, code, k_type):
        table_name = 'hist_' + k_type
        data = pd.read_sql_query(
            "SELECT code,`date`,close,ema_short,ema_long,dif,dea,macd FROM  " + table_name + " WHERE  code='" + code + "'",
            con=self.__engine)
        return data

    def merge_clmacd_result(self, id_time, bp_count, sp_count):
        engine = self.__engine
        session = sessionmaker(bind=engine)()
        result = ClmacdResult(id_time=id_time, bp_count=bp_count, sp_count=sp_count)
        session.merge(result)
        session.commit()
        session.close()

    def get_latest_bp(self, end_time):
        delta = timedelta(days=1)
        start_time = end_time - delta
        data = pd.read_sql_query(
            "SELECT * FROM clmacd_bp WHERE '" + start_time.strftime(
                '%Y-%m-%d %H:%M:%S') + "' < id_time AND id_time<='" + end_time.strftime(
                '%Y-%m-%d %H:%M:%S') + "' ORDER BY id_time",
            con=self.__engine)
        return data

    def get_latest_sp(self, end_time):
        delta = timedelta(days=1)
        start_time = end_time - delta
        data = pd.read_sql_query(
            "SELECT * FROM clmacd_sp WHERE '" + start_time.strftime(
                '%Y-%m-%d %H:%M:%S') + "' < id_time AND id_time<='" + end_time.strftime(
                '%Y-%m-%d %H:%M:%S') + "' ORDER BY id_time",
            con=self.__engine)
        return data

    def merge_clmacd_bp(self, id_time, code, price):
        engine = self.__engine
        session = sessionmaker(bind=engine)()
        bp = ClmacdBp(id_time=id_time, code=code, price=price)
        session.merge(bp)
        session.commit()
        session.close()

    def merge_clmacd_sp(self, id_time, code, price):
        engine = self.__engine
        session = sessionmaker(bind=engine)()
        sp = ClmacdSp(id_time=id_time, code=code, price=price)
        session.merge(sp)
        session.commit()
        session.close()


if __name__ == '__main__':
    try:
        base_db = BaseDB()
        st = datetime.strptime('2017-05-27 10:40:00', '%Y-%m-%d %H:%M:%S')
        # st = datetime.now()
        base_db.get_latest_bp(st)
    except Exception as e:
        print(":", e.__repr__())
