import multiprocessing
import random
import sys
import time

from tornado import concurrent


def read(q):
    # output.write('\r complete percent:%.0f%%' % (i / total * 100))

    time.sleep(random.random())


def main():
    futures = set()
    with concurrent.futures.ThreadPoolExecutor(multiprocessing.cpu_count() * 4) as executor:
        for q in (chr(ord('A') + i) for i in range(26)):
            future = executor.submit(read, q)
            output = sys.stdout
            output.write('\r Get %s from queue.' % q)
            futures.add(future)

        output.flush()
    try:
        for future in concurrent.futures.as_completed(futures):
            err = future.exception()
            if err is not None:
                raise err
    except KeyboardInterrupt:
        print("stopped by hand")

    print("stopped")


if __name__ == '__main__':
    main()
