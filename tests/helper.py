import os
from ksef_cli.ksef_conf import CONF


def set_os():
    os.environ[CONF.KSEFCONF_ENV] = os.path.join(
        os.path.dirname(__file__), 'conf', "kseftokens.yaml")
    # os.environ[CONF.KSEFDIR_ENV] = "/path/to/ksef_work_dir
