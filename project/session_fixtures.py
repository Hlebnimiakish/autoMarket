"""This module contains fixtures of session scope level, used in multiple tests"""

from unittest.mock import MagicMock

import pytest
# pylint: disable=consider-using-from-import
import user.views as views
from rest_framework.test import APIClient
from root.celery import app as celery_app
from root.common.views import CustomRequest


@pytest.fixture(scope='session', name='celery_config')
def celery_config():
    """Sets the test celery config to run tasks locally, in the
    same database with tests"""
    return {
        'task_always_eager': True
    }


@pytest.fixture(scope='session', name='client', autouse=True)
def get_client() -> APIClient:
    """Creates an instance of Django APIClient for tests"""
    return APIClient()


@pytest.fixture(scope='session', autouse=True)
def do_not_call_celery():
    """Creates mock imitating no celery workers being run, for
    some views not to send tasks to running celery worker during
    test session"""
    celery_inspect = celery_app.control.inspect()
    celery_inspect.active = MagicMock(return_value=False)


@pytest.fixture(scope='session', autouse=True)
def do_not_send_mail():
    """Creates mocks for mail sender functions, not to send emails on test
    email addresses and for custom request get_host function, as test APIClient
    do not have such a function and do not use 'host' address during tests"""
    views.user_verification_mail_sender = \
        MagicMock(return_value=None)
    views.password_reset_mail_sender = \
        MagicMock(return_value=None)
    CustomRequest.get_host = MagicMock(return_value='')
