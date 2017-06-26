# coding:utf-8
import logging

import tushare as ts
from sqlalchemy.types import String

from base_db import BaseDB

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(time)s] %(name)s:%(level)s: %(message)s"
)


class StockBaseFetcher:
    def __init__(self, db):
        self.__db = db

    '''
    更新列表
    '''

    def refresh_stock_list(self):
        engine = self.__db.get_engine()

        logging.info('fetching stock_basics')
        df = ts.get_stock_basics()
        df.to_sql('stock_basics', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        logging.info('fetching class_list_gem')
        gem = ts.get_gem_classified()
        gem.to_sql('class_list_gem', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        logging.info('fetching class_list_hs300')
        hs300 = ts.get_hs300s()
        hs300.to_sql('class_list_hs300', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        logging.info('fetching class_list_sz50')
        sz50 = ts.get_sz50s()
        sz50.to_sql('class_list_sz50', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        logging.info('fetching class_list_zz500')
        zz500 = ts.get_zz500s()
        zz500.to_sql('class_list_zz500', engine, if_exists='replace', index=True, dtype={'code': String(10)})

        self.__db.update_log_time('stock_list_fetch_time')


if __name__ == '__main__':
    base_db = BaseDB()
    sf = StockBaseFetcher(base_db)
    sf.refresh_stock_list()
