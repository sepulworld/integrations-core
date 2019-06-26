# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import sys

import pytest

from datadog_checks.base.utils.agent.memory import profile_memory


@pytest.mark.skipif(sys.version_info[0] < 3, reason='Memory profiling is only available on Python 3+')
def test_profile():
    pass
