# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# COMMONS
import logging
import time
from typing import Callable


def eval_time(function: Callable):
    """decorator to log the duration of the decorated method"""

    def timed(*args, **kwargs):
        log = logging.getLogger(__name__)
        time_start = time.time()
        result = function(*args, **kwargs)
        time_elapsed = round(time.time() - time_start, 2)

        log.info(f"Processing time of {function.__name__}: {time_elapsed}s")
        return result

    return timed
