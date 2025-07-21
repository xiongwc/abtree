import pytest
from abtree.core import status


def test_status_enum_values():
    assert status.Status.SUCCESS.name == "SUCCESS"
    assert status.Status.FAILURE.name == "FAILURE"
    assert status.Status.RUNNING.name == "RUNNING"
    assert str(status.Status.SUCCESS) == "SUCCESS"
    assert repr(status.Status.FAILURE) == "Status.FAILURE"


def test_policy_enum_values():
    assert status.Policy.SUCCEED_ON_ONE.name == "SUCCEED_ON_ONE"
    assert status.Policy.SUCCEED_ON_ALL.name == "SUCCEED_ON_ALL"
    assert status.Policy.FAIL_ON_ONE.name == "FAIL_ON_ONE"
    assert status.Policy.FAIL_ON_ALL.name == "FAIL_ON_ALL"
    assert str(status.Policy.SUCCEED_ON_ONE) == "SUCCEED_ON_ONE"
    assert repr(status.Policy.FAIL_ON_ALL) == "Policy.FAIL_ON_ALL"


def test_status_enum_iteration():
    all_statuses = {s.name for s in status.Status}
    assert all_statuses == {"SUCCESS", "FAILURE", "RUNNING"}


def test_policy_enum_iteration():
    all_policies = {p.name for p in status.Policy}
    assert all_policies == {"SUCCEED_ON_ONE", "SUCCEED_ON_ALL", "FAIL_ON_ONE", "FAIL_ON_ALL"} 