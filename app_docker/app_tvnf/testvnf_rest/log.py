import logging
import sys

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush
log.addHandler(handler)

