import configparser
import multiprocessing
import sys

import pandas as pd
import tushare as ts
from tornado import concurrent

import base_math as bm
from base_db import BaseDB


class DataFetcher:
    def __init__(self, db: BaseDB):
        super().__init__()
        self.__db = db
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')

    def fetch_hist_min_label_k_data_all(self, k_type):
        sys.stdout.write('fetching all data starting ...\n')
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

        sys.stdout.write('\nfetching all data ended\n')
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
            df_to_add.to_sql(table_name, self.__db.get_engine(), if_exists='append', index=False)
        except Exception as e:
            print(":", e.__str__(), code)


if __name__ == '__main__':
    base_db = BaseDB()
    sf = DataFetcher(base_db)
    sf.fetch_hist_min_label_k_data_all('30')
