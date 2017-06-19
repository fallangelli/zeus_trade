import configparser
import multiprocessing
import sys
from datetime import datetime

import pandas as pd
from tornado import concurrent

import base_math as bm
from base_db import BaseDB


def get_max_valid_date_between(df15: pd.DataFrame, df30: pd.DataFrame):
    s_df_30 = df30.sort_values(by=['date'], axis=0, ascending=False)
    for row in s_df_30['date'].values:
        if row in df15['date'].values:
            return row
    return ""


class CLMACDCalculator:
    def __init__(self, db: BaseDB):
        super().__init__()
        self.__db = db
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        self.__pool_size_cpu_times = cf.getint('thread_conf', 'pool_size_cpu_times')
        self.__time_count_30 = cf.getint('calc_parameter', 'time_count_30')

    def find_targets(self):
        sys.stdout.write(datetime.now().__str__() + '  finding targets starting ...\n')
        stock_list = self.__db.get_all_stock_list()
        list_size = stock_list.count()
        futures = set()
        df30 = self.__db.get_all_macd_data('30')
        df15 = self.__db.get_all_macd_data('15')
        i = 1
        with concurrent.futures.ThreadPoolExecutor(
                        multiprocessing.cpu_count() * self.__pool_size_cpu_times) as executor:
            for stock in stock_list:
                future = executor.submit(self.fit_30_pt, df15, df30, stock.code, self.__time_count_30, i, list_size)
                futures.add(future)
                i = i + 1

        sys.stdout.write(datetime.now().__str__() + 'finding targets ended\n')
        sys.stdout.flush()

    def fit_30_pt(self, df_15: pd.DataFrame, df_30: pd.DataFrame, code, time_count_30, curr, total):
        sys.stdout.write('\r calculating %s CLMACD, %d - %d' % (code, curr, total))
        backward_count = 21 + time_count_30
        try:
            df15 = df_15[df_15['code'] == code]
            df30 = df_30[df_30['code'] == code]
            if len(df_15) <= 1 or len(df_30) <= 1:
                print("code %s data length error" % code)
                return False
            df15.dropna()
            df30.dropna()

            max_date = get_max_valid_date_between(df15, df30)
            if max_date.strip() == '':
                print("code %s cann't get between date" % code)
                return False

            df15 = df15[df15['date'] <= max_date]
            df30 = df30[df30['date'] <= max_date]
            df15 = df15.sort_values(by=['date'], axis=0, ascending=False)
            df30 = df30.sort_values(by=['date'], axis=0, ascending=False)
            df30 = df30[0:backward_count + 1]
            df15 = df15[0:(backward_count + 1) * 2]

            self.fit_buy_30_pt(df15, df30, code, time_count_30)
            self.fit_sell_30_pt(df15, df30, code, time_count_30)
        except Exception as e:
            print(":", e.__repr__(), code)

    '''
    {30分敞口向上，0 轴上}
    DIF_MIN30:="MACD.DIFF#MIN30";
    DEAF_MIN30:="MACD.DEA#MIN30";
    MACD_MIN30:="MACD#MIN30";

    半小时敞口向上:= COUNT(MACD_MIN30>REF(MACD_MIN30,1),1)=1 and
     ((DIF_MIN30-DEAF_MIN30)>ABS(0.1*DEAF_MIN30));

    {15分底背离或双金叉}
    DIF_MIN15:="MACD.DIFF#MIN15";
    DEAF_MIN15:="MACD.DEA#MIN15";

    JCCOUNT15:=COUNT(CROSS(DIF_MIN15,DEAF_MIN15),BARSLAST(DEAF_MIN15>=0));
    二次金叉15M:=CROSS(DIF_MIN15,DEAF_MIN15) AND DEAF_MIN15<0 AND 
    COUNT(JCCOUNT15=2,21)=1;
    A1015:=BARSLAST(REF(CROSS(DIF_MIN15,DEAF_MIN15),1));
    底背离15M:=REF(CLOSE,A1015+1)>CLOSE AND DIF_MIN15>REF(DIF_MIN15,A1015+1) AND
     CROSS(DIF_MIN15,DEAF_MIN15);

    CON1:= 二次金叉15M and 底背离15M and 半小时敞口向上;
    XG1:IF(N>0,COUNT(REF(CON1,1)>0,N)>0,CON1);
    '''

    def fit_buy_30_pt(self, df15: pd.DataFrame, df30: pd.DataFrame, code, time_count_30):
        try:
            backward_count = 21 + time_count_30

            for index_30 in range(0, time_count_30):
                ret_j = 0
                # 半小时敞口向上 0 轴上
                up_30 = (df30['macd'].values[index_30] > df30['macd'].values[index_30 + 1] and
                         (df30['dif'].values[index_30] - df30['dea'].values[index_30]) > abs(
                             0.1 * df30['dea'].values[index_30])) and df30['macd'].values[index_30] > 0
                if not up_30:
                    continue

                up_15 = False
                for j in range(0, 2):
                    ret_j = 2 * index_30 + j
                    # 15分底背离
                    last_cross_index = bm.last_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                     df15['dea'][ret_j:(ret_j + 21)].values)
                    if last_cross_index >= backward_count:
                        continue
                    depart_tmp = df15['close'].values[last_cross_index] > df15['close'].values[ret_j] and \
                                 df15['dif'].values[ret_j] > df15['dif'].values[last_cross_index] and \
                                 bm.up_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                             df15['dea'][ret_j:(ret_j + 21)].values)
                    if not depart_tmp:
                        continue

                    # 二次金叉
                    if df15['dea'].values[ret_j] > 0:
                        continue

                    back_dea = df15['dea'][ret_j:(ret_j + 21)].values
                    last_index = bm.last_greater_0(back_dea)
                    if last_index <= 0:
                        continue

                    cross_count = bm.count_up_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                    df15['dea'][ret_j:(ret_j + 21)].values, last_index)
                    if cross_count >= 2:
                        up_15 = True
                        break

                if up_30 and up_15:
                    print("buy pt %s - 30M: %s , 15M: %s" % (
                        code, df30['date'].values[index_30], df15['date'].values[ret_j]))

                    self.__db.merge_clmacd_bp(id_time=df15['date'].values[ret_j], code=code,
                                              price=float(df15['close'].values[ret_j]))
        except Exception as e:
            print(":", e.__repr__(), code)

    '''
    {30分敞口向下，0 轴下}
    DIF_MIN30:="MACD.DIFF#MIN30";
    DEAF_MIN30:="MACD.DEA#MIN30";
    MACD_MIN30:="MACD#MIN30";

    半小时敞口向下:= COUNT(MACD_MIN30<REF(MACD_MIN30,1),1)=1 and
     ((DEAF_MIN30 - DIF_MIN30)>ABS(0.1*DEAF_MIN30)) and MACD_MIN30<0;

    {15分顶背离 双死叉}
    DIF_MIN15:="MACD.DIFF#MIN15";
    DEAF_MIN15:="MACD.DEA#MIN15";

    JCCOUNT15:=COUNT(CROSS(DIF_MIN15,DEAF_MIN15),BARSLAST(DEAF_MIN15>=0));
    二次死叉15M:=CROSS(DIF_MIN15,DEAF_MIN15) AND DEAF_MIN15>0 AND 
    COUNT(JCCOUNT15=2,21)=1;
    A1015:=BARSLAST(REF(CROSS(DIF_MIN15,DEAF_MIN15),1));
    顶背离15M:=REF(CLOSE,A1015+1)<CLOSE AND DIF_MIN15<REF(DIF_MIN15,A1015+1) AND
     CROSS(DIF_MIN15,DEAF_MIN15);

    CON1:= 二次死叉15M and 顶背离15M and 半小时敞口向下;
    XG1:IF(N>0,COUNT(REF(CON1,1)>0,N)>0,CON1);
    '''

    def fit_sell_30_pt(self, df15: pd.DataFrame, df30: pd.DataFrame, code, time_count_30):
        try:
            backward_count = 21 + time_count_30
            for index_30 in range(0, time_count_30):
                ret_j = 0
                # 半小时敞口向下 0 轴下
                down_30 = (df30['macd'].values[index_30] < df30['macd'].values[index_30 + 1] and
                           (df30['dea'].values[index_30] - df30['dif'].values[index_30]) > abs(
                               0.1 * df30['dea'].values[index_30])) and df30['macd'].values[index_30] < 0
                if not down_30:
                    continue

                down_15 = False
                for j in range(0, 2):
                    ret_j = 2 * index_30 + j
                    # 15分顶背离
                    last_cross_index = bm.last_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                     df15['dea'][ret_j:(ret_j + 21)].values)
                    if last_cross_index >= backward_count:
                        continue
                    depart_tmp = df15['close'].values[ret_j] > df15['close'].values[last_cross_index] and \
                                 df15['dif'].values[last_cross_index] > df15['dif'].values[ret_j] and \
                                 bm.down_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                               df15['dea'][ret_j:(ret_j + 21)].values)
                    if not depart_tmp:
                        continue

                    # 二次死叉
                    if df15['dea'].values[ret_j] < 0:
                        continue

                    back_dea = df15['dea'][ret_j:(ret_j + 21)].values
                    last_index = bm.last_less_0(back_dea)
                    if last_index <= 0:
                        continue

                    cross_count = bm.count_down_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                      df15['dea'][ret_j:(ret_j + 21)].values, last_index)
                    if cross_count >= 2:
                        down_15 = True
                        break

                if down_30 and down_15:
                    print("sell pt %s - 30M:  %s , 15M: %s" % (
                        code, df30['date'].values[index_30], df15['date'].values[ret_j]))

                    self.__db.merge_clmacd_sp(id_time=df15['date'].values[ret_j], code=code,
                                              price=float(df15['close'].values[ret_j]))

        except Exception as e:
            print(":", e.__repr__(), code)


if __name__ == '__main__':
    bd = BaseDB()
    cc = CLMACDCalculator(bd)
    cc.find_targets()

    # d30 = bd.get_macd_data('300652', '30')
    # d15 = bd.get_macd_data('300652', '15')
    # cc.fit_30_pt(d15, d30, '300652', 8, 1, 1)
