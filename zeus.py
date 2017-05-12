import logging
from datetime import datetime
from time import sleep

from base_db import BaseDB
from kdata_fetcher import KDataFetcher
from macd_filler import MACDFiller
from stock_base_fetcher import StockBaseFetcher

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(time)s] %(name)s:%(level)s: %(message)s"
)


class Zeus(object):
    def __init__(self, db: BaseDB, stock_base_fetcher: StockBaseFetcher, data_fetcher: KDataFetcher,
                 macd_filler: MACDFiller, step_interval=5):
        self.__db = db
        self.__step_interval = step_interval
        self.__data_fetcher = data_fetcher
        self.__stock_base_fetcher = stock_base_fetcher
        self.__macd_filler = macd_filler
        self.__market_close_time = datetime.now().replace(hour=15, minute=10, second=00)

    # 交易系统退出的条件, 如果判读符合条件,则退出交易系统
    def ready_to_exit(self):
        if datetime.now() > self.__market_close_time:
            logging.warning('现在不是交易时间, 自动退出交易, 如果需要改变退出条件,请修改 AutoTrade.py的ready_to_exit函数')
            return True
        return False

    def start(self):
        while not self.ready_to_exit():
            if self.__db.get_need_to_refresh_list():
                logging.info('超过一天未刷新列表，开始执行刷新!')
                self.__stock_base_fetcher.refresh_stock_list()

            logging.debug('updating data')
            sleep(self.__step_interval)

    '''
      更新低频后复权历史数据
      k_type - 默认为D日线数据
              D=日k线 W=周 M=月 
              5=5分钟 15=15分钟 
              30=30分钟 60=60分钟
      '''

    def update_k_data_with_macd(self, k_type):
        self.__data_fetcher.fetch_hist_min_label_k_data_all(k_type)
        self.__macd_filler.fill_macd_all(k_type)

        self.__db.update_log_time(2, 'all_hist_fetch_time')


if __name__ == '__main__':
    bd = BaseDB()
    sbf = StockBaseFetcher(bd)
    df = KDataFetcher(bd)
    mf = MACDFiller(bd)
    zeus = Zeus(bd, sbf, df, mf)
    # 开始运行
    zeus.start()
