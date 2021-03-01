import logging
log_level_dict = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARNING, "ERROR":logging.ERROR, "CRITICAL":logging.CRITICAL}

try:
    logging_level = log_level_dict["DEBUG"]
except:
    logging_level = logging.NOTSET

logging.basicConfig(level=logging_level, format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

logging.info("This is info")
logging.debug("This is debug")
logging.warning("This is warning")
logging.error("This is error")
logging.critical("This is critical")



