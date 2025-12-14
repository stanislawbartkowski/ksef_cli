import logging


def def_logger():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
