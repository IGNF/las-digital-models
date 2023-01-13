#!/bin/bash
python -m pytest ./test -s --log-cli-level INFO 2>&1 | tee pytest.log