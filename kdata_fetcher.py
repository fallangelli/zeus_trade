import configparser
import multiprocessing
import sys
from datetime import datetime

import pandas as pd
import tushare as ts
from tornado import concurrent

from base_db import BaseDB
from base_math import if_times


class KDataFetcher:
    def __init__(self, db: BaseDB):
        super().__init__()
        self.__db = db
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')

    def fetch_hist_min_label_k_data_all(self, k_type):
        sys.stdout.write(datetime.now().__str__() + 'fetching  ' + k_type + ' all data starting ...\n')
        stock_list = self.__db.get_all_stock_list()
        list_size = stock_list.count()
        futures = set()
        d_list = self.__db.get_all_date_list(k_type)
        i = 1
        with concurrent.futures.ThreadPoolExecutor(
                        multiprocessing.cpu_count() * self.__pool_size_cpu_times) as executor:
            for stock in stock_list:
                future = executor.submit(self.fetch_hist_min_label_k_data, d_list, stock.code, k_type, i,
                                         list_size)
                futures.add(future)
                i = i + 1

        sys.stdout.write(datetime.now().__str__() + 'fetching ' + k_type + '  all data ended\n')
        sys.stdout.flush()

    def fetch_hist_min_label_k_data(self, all_dates: pd.DataFrame, code, k_type, curr, total):
        sys.stdout.write('\r fetching %s hist %s k_data, %d - %d' % (code, k_type, curr, total))
        try:
            table_name = 'hist_' + k_type
            df = ts.get_k_data(code=code, autype='hfq', ktype=k_type, retry_count=20, pause=3)
            last_index = len(df) - 1
            if last_index > 1:
                if if_times(df['date'][last_index], k_type):
                    df = df.drop(last_index)

                stock_date = all_dates[all_dates['code'] == code]
                if len(stock_date) > 0:
                    max_date = stock_date['date'].max()
                    df = df[df['date'] > max_date]
                df.to_sql(table_name, self.__db.get_engine(), if_exists='append', index=False)
        except Exception as e:
            print(":", e.__repr__(), code)


if __name__ == '__main__':
    base_db = BaseDB()
    sf = KDataFetcher(base_db)
    sf.fetch_hist_min_label_k_data_all('30')
    sf.fetch_hist_min_label_k_data_all('15')

    # bd = base_db.get_macd_data('000066', '15')
    # sf.fetch_hist_min_label_k_data(bd, '000066', '15', 1, 1)
