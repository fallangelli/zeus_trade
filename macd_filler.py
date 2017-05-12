import configparser
import multiprocessing
import sys

import pandas as pd
from tornado import concurrent

import base_math as bm
from base_db import BaseDB


class MACDFiller:
    def __init__(self, db: BaseDB):
        super().__init__()
        self.__db = db
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')

    def fill_macd_all(self, k_type):
        sys.stdout.write('filling all macd starting ...\n')
        stock_list = self.__db.get_all_stock_list()
        list_size = stock_list.count()
        futures = set()
        d_list = self.__db.get_data_need_to_macd(k_type)
        i = 1
        with concurrent.futures.ThreadPoolExecutor(
                        multiprocessing.cpu_count() * self.__pool_size_cpu_times) as executor:
            for stock in stock_list:
                future = executor.submit(self.fill_macd, d_list, stock.code, k_type, i, list_size)
                futures.add(future)
                i = i + 1

        sys.stdout.write('\nfilling all macd ended\n')
        sys.stdout.flush()

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
                                    short_l=base['ema_short'].get(0), long_l=base['ema_long'].get(0),
                                    dea_l=base['dea'].get(0))

            table_name = 'hist_' + k_type
            sql = ''
            for index, row in macd_list.iterrows():
                sql = sql + "UPDATE %s SET ema_short=%f,ema_long=%f,dea=%f,dif=%f,macd=%f WHERE date='%s' and " \
                            "code='%s';" % (table_name, row['ema_short'], row['ema_long'], row['dea'], row['dif'],
                                            row['macd'], row['date'], code)
            self.__db.get_engine().execute(sql)

        except Exception as e:
            print(":", e.__repr__(), code)


if __name__ == '__main__':
    base_db = BaseDB()
    mf = MACDFiller(base_db)
    bd = base_db.get_macd_data('000001', '30')
    mf.fill_macd(bd, '000001', '30', 1, 1)

    # mf.fill_macd_all('30')
