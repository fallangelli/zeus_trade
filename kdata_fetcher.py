# coding:utf-8
import multiprocessing
import sys
from datetime import datetime

import configparser
import numpy as np
import pandas as pd
import talib as ta
import tushare as ts
from tornado import concurrent

from base_db import BaseDB
from base_math import if_times


class KDataFetcher:
    def __init__(self, db):
        self.__db = db
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')

    def fetch_hist_min_label_k_data_all(self, k_type):
        sys.stdout.write(datetime.now().__str__() + 'fetching  ' + k_type + ' all data starting ...\n')
        stock_list = self.__db.get_all_stock_list()
        list_size = stock_list.count()
        futures = set()

        i = 1
        with concurrent.futures.ThreadPoolExecutor(
                        multiprocessing.cpu_count() * self.__pool_size_cpu_times) as executor:
            for stock in stock_list:
                future = executor.submit(self.fetch_hist_min_label_k_data, stock.code, k_type, i,
                                         list_size)
                futures.add(future)
                i = i + 1

        sys.stdout.write(datetime.now().__str__() + 'fetching ' + k_type + '  all data ended\n')
        sys.stdout.flush()

    def fetch_hist_min_label_k_data(self, code, k_type, curr, total):
        sys.stdout.write('\r fetching %s hist %s k_data, %d - %d' % (code, k_type, curr, total))
        try:
            table_name = 'hist_' + k_type
            df = ts.get_k_data(code=code, autype='qfq', ktype=k_type, retry_count=20, pause=3)
            if len(df) < 80:
                return

            last_index = len(df) - 1
            if not if_times(df['date'][last_index], k_type):
                df = df.drop(last_index)

            macd_dif, macd_dea, macd_val = ta.MACDEXT(np.array(df['close']), fastperiod=12, fastmatype=1, slowperiod=26,
                                                      slowmatype=1, signalperiod=9, signalmatype=1)
            macd_val = macd_val * 2
            df['dif'] = pd.Series(macd_dif, index=df.index)
            df['dea'] = pd.Series(macd_dea, index=df.index)
            df['macd'] = pd.Series(macd_val, index=df.index)
            remain_count = 40;
            if k_type == '15':
                remain_count = 80
            df1 = df[(len(df) - remain_count):len(df)]
            df1.to_sql(table_name, self.__db.get_engine(), if_exists='append', index=False)
        except Exception as e:
            print(":", e.__repr__(), code)


if __name__ == '__main__':
    base_db = BaseDB()
    sf = KDataFetcher(base_db)
    # sf.fetch_hist_min_label_k_data_all('30')
    # sf.fetch_hist_min_label_k_data_all('15')

    # bd = base_db.get_macd_data('000066', '15')
    sf.fetch_hist_min_label_k_data(base_db, '000066', '30', 1, 1)
