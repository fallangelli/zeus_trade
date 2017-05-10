import configparser
import logging
import multiprocessing
import sys
from datetime import datetime
from time import sleep

import pandas as pd
import tushare as ts
from sqlalchemy import Column
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer, String, DateTime
from tornado import concurrent

import base_math as bm

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

BaseModel = declarative_base()


class TimeLog(BaseModel):
    __tablename__ = 'time_log'
    id = Column(Integer, primary_key=True)
    type = Column(String(30))
    last_modify_time = Column(DateTime())


class StockBasics(BaseModel):
    __tablename__ = 'stock_basics'
    code = Column(String(30), primary_key=True)


class ZeusDB:
    def __init__(self):
        super().__init__()

        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        username = cf.get('db_conf', 'username')
        password = cf.get('db_conf', 'password')
        server = cf.get('db_conf', 'server')
        database = cf.get('db_conf', 'database')

        self.__thread_pool_size = cf.getint('thread_conf', 'thread_pool_size')

        self.__engine = create_engine(
            'mysql+pymysql://' + username + ':' + password + '@' + server + '/' + database + '?charset=utf8',
            pool_size=1024, pool_recycle=3600)
        session = sessionmaker(bind=self.__engine)
        self.__session = session()

    def __del__(self):
        self.__session.close()

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

        time_log = TimeLog(id=1, type='stock_list_fetch_time', last_modify_time=datetime.now())
        self.__session.merge(time_log)
        self.__session.commit()

    '''
    更新低频后复权历史数据
    k_type - 默认为D日线数据
            D=日k线 W=周 M=月 
            5=5分钟 15=15分钟 
            30=30分钟 60=60分钟
    '''

    def update_k_data_with_macd(self, k_type):
        list_size = self.__session.query(func.count('*')).select_from(StockBasics).scalar()
        query = self.__session.query(StockBasics)
        logging.info('sync started')
        futures = set()
        i = 0
        output = sys.stdout
        with concurrent.futures.ThreadPoolExecutor(multiprocessing.cpu_count() * 4) as executor:
            for stock in query:
                future = executor.submit(self.fetch_hist_k_data_with_macd, stock.code, k_type)
                futures.add(future)
                output.write('\r complete percent:%.0f%%' % (i % list_size) * 100)
                i = i + 1
                if i > 10: break
            output.write('\n')
            output.flush()

        time_log = TimeLog(id=2, type='all_hist_fetch_time', last_modify_time=datetime.now())
        self.__session.merge(time_log)
        self.__session.commit()
        logging.info('sync ended')

    def get_all_stock_list(self):
        return self.__session.query(StockBasics)

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
        query = self.__session.query(TimeLog)
        last_fetch_time = query.filter(TimeLog.id == 1).first().last_modify_time
        print('last_fetch_time:', last_fetch_time)

        if (datetime.now() - last_fetch_time).days > 1:
            return True
        return False

    def fetch_hist_k_data_with_macd(self, code, k_type):
        self.fetch_hist_min_label_k_data(code, k_type)
        sleep(0.1)
        self.fill_macd(code, k_type)
        # logging.debug('fetched %s his %s k_data with macd. %d of %d',code,k_type,index,size)

    def fetch_hist_min_label_k_data(self, code, k_type):
        table_name = 'hist_' + k_type
        conn = self.__engine.connect()

        try:
            sql = "select `date` from %s where code = '%s'" % (table_name, code)
            db_results = conn.execute(sql).fetchall()
            results = [db_result[0] for db_result in db_results]

            df = ts.get_k_data(code, autype='hfq', ktype=k_type)
            if len(df) <= 0:
                return

            if not bm.if_times(df.tail(1)['date'].to_string(), k_type):
                df = df.drop(len(df) - 1)

            list_to_add = []
            for index, row in df.iterrows():
                if not row['date'] in results:
                    list_to_add.append(row)

            df_to_add = pd.DataFrame(list_to_add)
            df_to_add.to_sql(table_name, self.__engine, if_exists='append', index=False)
        except Exception as e:
            print(":", e, code)

    def get_date_need_to_macd(self, code, k_type):
        table_name = 'hist_' + k_type
        data = pd.read_sql_query("SELECT b.* FROM (\
         SELECT date,close,ema_short,ema_long,dif,dea,macd FROM " + table_name + " \
         WHERE date = (SELECT max(date) FROM " + table_name + " \
         WHERE macd IS NOT NULL AND code = '" + code + "') AND code = '" + code + "'  \
         UNION \
         SELECT date,close,ema_short,ema_long,dif,dea,macd FROM " + table_name + " \
         WHERE date >= (SELECT min(date) FROM " + table_name + " \
         WHERE macd IS NULL AND code = '" + code + "') AND code = '" + code + "'  \
         ) b\
         ORDER BY b.date", con=self.__engine)
        return data

    def fill_macd(self, code, k_type):
        try:
            df = zeus_db.get_date_need_to_macd(code, k_type)
            if len(df) <= 0:
                return

            base = df[:1]
            if base['macd'] is None:
                macd_list = bm.macd(df['date'].values, df['close'].values)
            else:
                df = df.drop(0)
                if len(df) <= 0:
                    return
                macd_list = bm.macd(df['date'].values, df['close'].values,
                                    base['ema_short'][0], base['ema_long'][0], base['dea'][0])

            conn = self.__engine.connect()
            table_name = 'hist_' + k_type
            for index, row in macd_list.iterrows():
                sql = "UPDATE %s SET ema_short=%f,ema_long=%f,dea=%f,dif=%f,macd=%f WHERE date='%s' and code='%s'" \
                      % (table_name, row['ema_short'], row['ema_long'], row['dea'], row['dif'], row['macd'],
                         row['date'],
                         code)
                conn.execute(sql)
        except Exception as e:
            print(":", e, code)

    def get_close_list(self, code, k_type):
        table_name = 'hist_' + code + '_' + k_type
        data = pd.read_sql_query('SELECT date,close FROM ' + table_name, con=self.__engine)
        return data

    def get_limit_close_list(self, code, k_type, limit):
        table_name = 'hist_' + code + '_' + k_type
        data = pd.read_sql_query('SELECT * FROM (SELECT date,close FROM ' + table_name + ' \
         ORDER BY date DESC LIMIT ' + str(limit) + ') t \
         ORDER BY t.date ASC', con=self.__engine)
        return data


if __name__ == '__main__':
    zeus_db = ZeusDB()
    # zeus_db.refresh_stock_list()
    #    zeus_db.fetch_all_hist_k_data('30')
    # print(zeus_db.IfKTypeTimes('2017-04-27 11:05','15'))
    # zeus_db.fetch_hist_k_data('600809','15')
    #    zeus_db.fetch_hist_min_lable_k_data('600809','15')
    #    zeus_db.fetch_hist_min_lable_k_data('600809','30')
    #    cp = zeus_db.GetClosePrice('600820','30')
    #    macd_list = bm.MACD(cp['close'])
    #    print(macd_list)
    #    macd_list = EMA(cp['close'],12)
    #    print(macd_list)
    # cp = zeus_db.fetch_hist_k_data_with_macd('600809', '30')
    # cp = zeus_db.FillMACD('000001', '30')
    # zeus_db.update_k_data_with_macd('15')
    zeus_db.update_k_data_with_macd('30')
