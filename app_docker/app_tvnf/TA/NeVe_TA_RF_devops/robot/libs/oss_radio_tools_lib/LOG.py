# __author__ = 'x5luo'
import logging


class LOG(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='ConfigureSBTSDNS.log',
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # ????????
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        # ?????console??handler???root logger
        logging.getLogger('').addHandler(console)
