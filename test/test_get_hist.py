import multiprocessing
import sys
import time

from tornado import concurrent


def read(q):
    output = sys.stdout
    output.write('\r complete percent:%.0f%%' % q)
    time.sleep(3)


def main():
    futures = set()
    output = sys.stdout
    with concurrent.futures.ThreadPoolExecutor(multiprocessing.cpu_count() * 56) as executor:
        for i in range(260):
            future = executor.submit(read, i)
            futures.add(future)

    # try:
    #     for future in concurrent.futures.as_completed(futures):
    #         err = future.exception()
    #         if err is not None:
    #             raise err
    # except KeyboardInterrupt:
    #     print("stopped by hand")
    output.write('\n')
    output.flush()
    print("stopped")


if __name__ == '__main__':
    main()
