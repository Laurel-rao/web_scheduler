import logging
import os
import time

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

log_err_file = os.path.join(os.path.dirname(__file__), "logger_err_%s.log" % time.strftime("%Y_%m_%d"))
log_file = os.path.join(os.path.dirname(__file__), "logger_%s.log" % time.strftime("%Y_%m_%d"))
fh_err = logging.FileHandler(log_err_file)
fh = logging.FileHandler(log_file)

fh_err.setLevel(logging.ERROR)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - [%(pathname)s:%(lineno)d] - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
#
fh_err.setFormatter(formatter)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh_err)
logger.addHandler(fh)
logger.addHandler(ch)