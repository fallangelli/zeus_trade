# coding:utf-8
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from base_db import BaseDB
from base_mail import ZeusMail
from clmacd_calcuter import CLMACDCalculator
from kdata_fetcher import KDataFetcher
from macd_filler import MACDFiller
from stock_base_fetcher import StockBaseFetcher

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(time)s] %(name)s:%(level)s: %(message)s"
)


class Zeus(object):
    def __init__(self, db, stock_base_fetcher, data_fetcher,
                 macd_filler, cl_calculator, step_interval=5):
        self.__db = db
        self.__scheduler = BlockingScheduler()
        self.__step_interval = step_interval
        self.__data_fetcher = data_fetcher
        self.__stock_base_fetcher = stock_base_fetcher
        self.__macd_filler = macd_filler
        self._cl_calculator = cl_calculator
        self.__market_close_time = datetime.now().replace(hour=15, minute=10, second=00)

    # 交易系统退出的条件, 如果判读符合条件,则退出交易系统
    def ready_to_exit(self):
        if datetime.now() > self.__market_close_time:
            logging.warning('现在不是交易时间, 自动退出交易, 如果需要改变退出条件,请修改 AutoTrade.py的ready_to_exit函数')
            return True
        return False

    def start(self):
        # 每周3更新列表
        self.__scheduler.add_job(self.refresh_stock_list, 'cron', day_of_week='2')

        # 工作日10:31,13:31更新数据，计算趋势和B/S目标
        self.__scheduler.add_job(self.refresh_targets, 'cron', day_of_week='0-4', hour='23',
                                 minute='59')
        try:
            self.__scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.__scheduler.shutdown()

    def refresh_stock_list(self):
        logging.info('refreshing stock list data')
        self.__stock_base_fetcher.refresh_stock_list()

    def refresh_targets(self, end_time=None):
        logging.info('fetching all hist min k_data data with macd')
        self.__data_fetcher.fetch_hist_min_label_k_data_all('30')
        self.__data_fetcher.fetch_hist_min_label_k_data_all('15')
        self.__macd_filler.fill_macd_all('30')
        self.__macd_filler.fill_macd_all('15')
        self.__db.update_log_time('all_hist_with_macd_fetch_time')

        logging.info('moving out date data')
        self.__db.move_out_date_data()

        logging.info('finding fit 30 CLMACD targets')
        self._cl_calculator.find_targets()

        curr_time = datetime.now()
        if end_time is not None:
            curr_time = end_time

        latest_bp = self.__db.get_latest_bp(curr_time)
        latest_sp = self.__db.get_latest_sp(curr_time)
        self.__db.merge_clmacd_result(curr_time, len(latest_bp), len(latest_sp))
        self.__db.update_log_time('last_merge_clmacd_result_time')

        mail = ZeusMail()
        mail.send_mail(curr_time, latest_bp, latest_sp)


if __name__ == '__main__':
    bd = BaseDB()
    sbf = StockBaseFetcher(bd)
    df = KDataFetcher(bd)
    mf = MACDFiller(bd)
    cc = CLMACDCalculator(bd)

    zeus = Zeus(bd, sbf, df, mf, cc)
    # zeus.refresh_stock_list()
    # zeus.refresh_targets()

    # st = datetime.strptime('2017-06-01 16:05:00', '%Y-%m-%d %H:%M:%S')
    # zeus.refresh_targets(st)

    # 开始运行
    zeus.start()
