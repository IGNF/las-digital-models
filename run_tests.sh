#!/bin/bash
python -m pytest ./test -s 2>&1 | tee pytest.log