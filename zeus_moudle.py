import sys
import time

import base_math
from zeus_db import ZeusDB

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


def fit_buy_30_pt(code, time_count_30):
    backward_count = 21 + time_count_30
    db = ZeusDB()
    ret_val = False

    max_date = db.get_max_macd(code)
    if max_date is None:
        return False

    df30 = db.get_latest_macd(code, '30', max_date, backward_count)
    if len(df30) <= 0:
        return False
    df15 = db.get_latest_macd(code, '15', max_date, backward_count * 2)
    if len(df15) <= 0:
        return False

    for index_30 in range(0, time_count_30):
        ret_j = 0
        # 半小时敞口向上
        up_30 = df30['macd'][index_30] > df30['macd'][index_30 + 1] \
                and (df30['dif'][index_30] - df30['dea'][index_30]) > abs(0.1 * df30['dea'][index_30])
        if not up_30:
            continue

        up_15 = False
        for j in range(0, 2):
            ret_j = 2 * index_30 + j
            # 15分底背离
            last_cross_index = base_math.last_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                    df15['dea'][ret_j:(ret_j + 21)].values)
            if last_cross_index >= backward_count:
                break
            depart_tmp = df15['close'][last_cross_index] > df15['close'][ret_j] and df15['dif'][ret_j] > df15['dif'][
                last_cross_index] and base_math.up_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                         df15['dea'][ret_j:(ret_j + 21)].values)
            if not depart_tmp:
                continue

            # 二次金叉
            back_dea = df15['dif'][ret_j:(ret_j + 21)].values
            last_index = base_math.last_greater_0(back_dea)
            if last_index <= 0:
                continue

            cross_count = base_math.count_up_cross(df15['dif'][ret_j:(ret_j + 21)].values,
                                                   df15['dea'][ret_j:(ret_j + 21)].values, last_index)
            if cross_count >= 2:
                up_15 = True
                break

        if up_30 and up_15:
            print("%s - 30M: %s , 15M: %s" % (code, df30['date'][index_30], df15['date'][ret_j]))
            ret_val = True

    return ret_val


if __name__ == '__main__':
    zeus_db = ZeusDB()
    query = zeus_db.get_all_stock_list()
    total = query.count()

    print('analysis start time : %s' % time.strftime('%Y-%m-%d %H:%M:%S'))

    # futures = set()
    # output = sys.stdout
    # i = 0
    # with concurrent.futures.ThreadPoolExecutor(multiprocessing.cpu_count() * 4) as executor:
    #     for stock in query:
    #         future = executor.submit(fit_buy_30_pt, stock.code,12)
    #         futures.add(future)
    #         output.write('\r complete percent:%.0f%%' % (i / total * 100))
    #         i = i + 1
    #     output.write('\n')
    #     output.flush()

    i = 0
    output = sys.stdout
    for stock in query:
        fit_buy_30_pt(stock.code, 12)
        output.write('\r complete percent:%.0f%%' % (i / total * 100))
        i = i + 1
    output.flush()

    # fit_buy_30_pt('000008', 8)

    print('end time : %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
    #        if moudle.fit_buy_30_pt(stock.code,8):
    #            print(stock.code)
    #    moudle.fit_buy_30_pt('000584',64)
