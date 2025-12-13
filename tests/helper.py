import os
from ksef_cli.ksef_conf import CONF


def CO():
    conf_path = os.path.join(os.path.dirname(
        __file__), 'conf', "kseftokens.yaml")
    work_dir = os.path.join(os.path.dirname(__file__), 'worktemp')
    return CONF(conf_path, work_dir)
