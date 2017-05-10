import logging
from datetime import datetime
from time import sleep

from zeus_db import ZeusDB

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(time)s] %(name)s:%(level)s: %(message)s"
)


class Zeus(object):
    def __init__(self, db, step_interval=5):
        self.__zeus_db = db
        self.__step_interval = step_interval
        self.__current_time = datetime.now()
        self.__market_close_time = datetime.now().replace(hour=15, minute=10, second=00)

    # 交易系统退出的条件, 如果判读符合条件,则退出交易系统
    def ready_to_exit(self):
        if self.__current_time > self.__market_close_time:
            logging.warning('现在不是交易时间, 自动退出交易, 如果需要改变退出条件,请修改 AutoTrade.py的ready_to_exit函数')
            return True
        return False

    def start(self):
        while not self.ready_to_exit():
            if self.__zeus_db.need_to_refresh_list():
                logging.info('超过一天未刷新列表，开始执行刷新!')
                self.__zeus_db.refresh_stock_list()

            self.__current_time = datetime.now()
            logging.debug('updating data')
            sleep(self.__step_interval)


if __name__ == '__main__':
    zeus_db = ZeusDB()
    zeus = Zeus(db=zeus_db)
    # 开始运行
    zeus.start()
