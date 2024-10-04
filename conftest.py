from typing import Dict
import pytest
from pytest import StashKey, CollectReport

phase_report_key = StashKey[Dict[str, CollectReport]]()


# See 'Making test result information available in fixtures'
# from pytest docs for an indepth explanation of this hook
@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    rep = yield

    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep
    print("In hook")
    return rep
