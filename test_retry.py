import pytest
from botocore.exceptions import ClientError
from mock import MagicMock
from retrying import retry

RATE_LIMIT_RESPONSE = {
    'Error': {
        'Code': 'RateLimitExceeded',
        'Message':
        'Your requests have exceeded the rate limit. Please try again.'}
}

RATE_LIMIT_ERROR = ClientError(
    RATE_LIMIT_RESPONSE,
    'DescribeInstances')


class AWSClass(object):

    def list_instances(self):
        pass

    @retry
    def list_instances_with_retry(self):
        return self.list_instances()

    @retry(stop_max_attempt_number=3)
    def list_instances_with_3_attempts(self):
        return self.list_instances()

    @retry(stop_max_attempt_number=3)
    def list_instances_catch_exceptions_with_3_attempts(self):
        try:
            return self.list_instances()
        except Exception as e:
            return None


def test_expect_no_exception():
    aws_instance = AWSClass()
    aws_instance.list_instances = MagicMock(
        side_effect=RATE_LIMIT_ERROR)
    aws_instance.list_instances_catch_exceptions_with_3_attempts()
    assert aws_instance.list_instances.call_count == 1


def test_expect_exception():
    aws_instance = AWSClass()
    aws_instance.list_instances = MagicMock(
        side_effect=RATE_LIMIT_ERROR)
    with pytest.raises(ClientError):
        aws_instance.list_instances()



def test_expect_2_attempts():
    aws_instance = AWSClass()
    aws_instance.list_instances = MagicMock(
        side_effect=[
            RATE_LIMIT_ERROR,
            [1, 2, 3]])
    aws_instance.list_instances_with_retry()
    assert aws_instance.list_instances.call_count == 2


def test_expect_failure_after_3_attempts():
    aws_instance = AWSClass()
    aws_instance.list_instances = MagicMock(
        side_effect=RATE_LIMIT_ERROR)
    with pytest.raises(ClientError):
        aws_instance.list_instances_with_3_attempts()
    assert aws_instance.list_instances.call_count == 3
