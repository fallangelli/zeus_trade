import configparser
import logging
import multiprocessing
import sys
from datetime import datetime

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import String
from tornado import concurrent

import base_math as bm
from base_model import TimeLog, StockBasic

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


class ZeusDB:
    def __init__(self):
        super().__init__()

        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        username = cf.get('db_conf', 'username')
        password = cf.get('db_conf', 'password')
        server = cf.get('db_conf', 'server')
        database = cf.get('db_conf', 'database')

        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')

        self.__engine = create_engine(
            'mysql+pymysql://' + username + ':' + password + '@' + server + '/' + database + '?charset=utf8',
            pool_size=128, pool_recycle=300)

    '''
    更新列表
    '''

    def refresh_stock_list(self):
        engine = self.__engine

        df = ts.get_stock_basics()
        df.to_sql('stock_basics', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        gem = ts.get_gem_classified()
        gem.to_sql('class_list_gem', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        hs300 = ts.get_hs300s()
        hs300.to_sql('class_list_hs300', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        sz50 = ts.get_sz50s()
        sz50.to_sql('class_list_sz50', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        zz500 = ts.get_zz500s()
        zz500.to_sql('class_list_zz500', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        session = sessionmaker(bind=engine)()
        time_log = TimeLog(id=1, type='stock_list_fetch_time', last_modify_time=datetime.now())
        session.merge(time_log)
        session.commit()
        session.close()

    '''
    更新低频后复权历史数据
    k_type - 默认为D日线数据
            D=日k线 W=周 M=月 
            5=5分钟 15=15分钟 
            30=30分钟 60=60分钟
    '''

    def update_k_data_with_macd(self, k_type):
        self.fetch_hist_min_label_k_data_all(k_type)
        self.fill_macd_all(k_type)

        session = sessionmaker(bind=self.__engine)()
        time_log = TimeLog(id=2, type='all_hist_fetch_time', last_modify_time=datetime.now())
        session.merge(time_log)
        session.commit()
        session.close()

    def fetch_hist_min_label_k_data_all(self, k_type):
        sys.stdout.write('fetching all data starting ...\n')
        stock_list = self.get_all_stock_list()
        list_size = stock_list.count()
        futures = set()
        d_list = self.get_all_date_list(k_type)
        i = 1
        with concurrent.futures.ThreadPoolExecutor(
                        multiprocessing.cpu_count() * self.__pool_size_cpu_times) as executor:
            for stock in stock_list:
                future = executor.submit(self.fetch_hist_min_label_k_data, d_list, stock.code, k_type, i,
                                         list_size)
                futures.add(future)
                i = i + 1

        sys.stdout.write('\nfetching all data ended\n')
        sys.stdout.flush()

    def fill_macd_all(self, k_type):
        sys.stdout.write('filling all macd starting ...\n')
        stock_list = self.get_all_stock_list()
        list_size = stock_list.count()
        futures = set()
        d_list = self.get_data_need_to_macd(k_type)
        i = 1
        with concurrent.futures.ThreadPoolExecutor(
                        multiprocessing.cpu_count() * self.__pool_size_cpu_times) as executor:
            for stock in stock_list:
                future = executor.submit(self.fill_macd, d_list, stock.code, k_type, i, list_size)
                futures.add(future)
                i = i + 1

        sys.stdout.write('\nfilling all macd ended\n')
        sys.stdout.flush()

    def fetch_hist_min_label_k_data(self, all_dates: pd.DataFrame, code, k_type, curr, total):
        sys.stdout.write('\r fetching %s hist %s k_data, %d - %d' % (code, k_type, curr, total))
        try:
            stock_date = all_dates[all_dates['code'] == code]
            list_date = stock_date['date'].values
            if len(list_date) <= 1:
                return
            table_name = 'hist_' + k_type

            df = ts.get_k_data(code, autype='hfq', ktype=k_type)
            if len(df) <= 0:
                return

            list_to_add = []
            for index, row in df.iterrows():
                if not bm.if_times(row['date'], k_type):
                    continue
                if not row['date'] in list_date:
                    list_to_add.append(row)
            if len(list_to_add) <= 0:
                return

            df_to_add = pd.DataFrame(list_to_add)
            df_to_add.to_sql(table_name, self.__engine, if_exists='append', index=False)
        except Exception as e:
            print(":", e.__str__(), code)

    def fill_macd(self, all_data: pd.DataFrame, code, k_type, curr, total):
        sys.stdout.write('\r filling %s hist %s macd, %d - %d' % (code, k_type, curr, total))
        try:
            stock_data = all_data[all_data['code'] == code]

            if len(stock_data) <= 1:
                return
            base = stock_data[:1]

            if base['macd'].get(0) is None:
                macd_list = bm.macd(d=stock_data['date'].values, x=stock_data['close'].values)
            else:
                data = stock_data.drop(0)
                if len(data) <= 0:
                    return
                macd_list = bm.macd(d=data['date'].values, x=data['close'].values,
                                    short_l=base['ema_short'][0], long_l=base['ema_long'][0], dea_l=base['dea'][0])

            table_name = 'hist_' + k_type
            sql = ''
            for index, row in macd_list.iterrows():
                sql = sql + "UPDATE %s SET ema_short=%f,ema_long=%f,dea=%f,dif=%f,macd=%f WHERE date='%s' and " \
                            "code='%s';" % (table_name, row['ema_short'], row['ema_long'], row['dea'], row['dif'],
                                            row['macd'], row['date'], code)
            self.__engine.execute(sql)

        except Exception as e:
            print(":", e.__str__(), code)

    def get_all_stock_list(self):
        session = sessionmaker(bind=self.__engine)()
        ret_list = session.query(StockBasic)
        session.close()
        return ret_list

    def get_latest_macd(self, code, k_type, max_date, count=8):
        table_name = 'hist_' + k_type
        data = pd.read_sql_query(
            "SELECT b.* FROM ( SELECT `date`,close,dif,dea,macd FROM  " +
            table_name + " WHERE date <= '" + max_date + "' AND code='" +
            code + "' ORDER BY date DESC  LIMIT " + str(count) + ") b ", con=self.__engine)
        return data

    def get_max_macd(self, code):
        sql = "select min(c.md) from (\
                 select max(`date`) md from hist_30 where code = '%s'\
                 union\
                 select max(`date`) md from hist_15 where code = '%s'\
                 ) c" % (code, code)
        max_date = pd.read_sql_query(sql, con=self.__engine)
        return max_date.values[0][0]

    def need_to_refresh_list(self):
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

    def get_close_list(self, code, k_type):
        table_name = 'hist_' + code + '_' + k_type
        ret_val = pd.read_sql_query('SELECT date,close FROM ' + table_name, con=self.__engine)
        return ret_val

    def get_limit_close_list(self, code, k_type, limit):
        table_name = 'hist_' + code + '_' + k_type
        data = pd.read_sql_query('SELECT * FROM (SELECT date,close FROM ' + table_name + ' \
                 ORDER BY date DESC LIMIT ' + str(limit) + ') t \
                 ORDER BY t.date ASC', con=self.__engine)
        return data


if __name__ == '__main__':
    zeus_db = ZeusDB()
    # zeus_db.refresh_stock_list()

    date_list = zeus_db.get_all_date_list('15')
    zeus_db.fetch_hist_min_label_k_data(date_list, '000001', '15', 1, 1)
    # data = zeus_db.get_data_need_to_macd('30')
    # zeus_db.fill_macd(data, '603399', '30', 1, 1)
    # zeus_db.update_k_data_with_macd('15')
