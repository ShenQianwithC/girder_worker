from girder_worker.utils import JobStatus
import pytest


# This may create custom statuses that it is hard to test for.
# Make sure we check that we have at least the expected
# standard statuses
@pytest.mark.parametrize('endpoint,standard_statuses', [
    ('integration_tests/traditional/test_job_girder_worker_run',
     [JobStatus.QUEUED,
      JobStatus.RUNNING,
      JobStatus.SUCCESS]),
    ('integration_tests/traditional/test_girder_worker_run_as_celery_task',
     [JobStatus.RUNNING,
      JobStatus.SUCCESS])], ids=['traditional', 'celery'])
def test_girder_worker_run(session, api_url, wait_for_success, get_result,
                           endpoint, standard_statuses):
    r = session.post(api_url(endpoint))
    assert r.status_code == 200

    with wait_for_success(r.json()['_id']) as job:

        assert [ts['status'] for ts in job['timestamps']
                if ts['status'] in standard_statuses] == standard_statuses

        assert 'celeryTaskId' in job
        assert get_result(job['celeryTaskId']) == '{"c": {"data": 3, "format": "integer"}}'


# Note: This may create custom statuses that it is hard to test for.
# Make sure we check that we have at least the expected
# standard statuses
@pytest.mark.parametrize('endpoint,standard_statuses', [
    ('integration_tests/traditional/test_job_girder_worker_run_fails',
     [JobStatus.QUEUED,
      JobStatus.RUNNING,
      JobStatus.ERROR]),
    ('integration_tests/traditional/test_girder_worker_run_as_celery_task_fails',
     [JobStatus.RUNNING,
      JobStatus.ERROR])], ids=['traditional', 'celery'])
def test_girder_worker_run_fails(session, api_url, wait_for_error,
                                 endpoint, standard_statuses):
    r = session.post(api_url(endpoint))
    assert r.status_code == 200

    with wait_for_error(r.json()['_id']) as job:
        assert [ts['status'] for ts in job['timestamps']
                if ts['status'] in standard_statuses] == standard_statuses

        assert job['log'][0].startswith('Exception: invalid syntax (<string>, line 1)')


def test_custom_task_name(session, api_url, wait_for_success, get_result):
    r = session.post(api_url('integration_tests/traditional/test_job_custom_task_name'))
    assert r.status_code == 200

    with wait_for_success(r.json()['_id']) as job:
        assert [ts['status'] for ts in job['timestamps']] == \
            [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.SUCCESS]

        assert 'celeryTaskId' in job
        assert get_result(job['celeryTaskId']) == '6765'


def test_custom_task_name_fails(session, api_url, wait_for_error, get_result):
    r = session.post(api_url('integration_tests/traditional/test_job_custom_task_name_fails'))
    assert r.status_code == 200

    with wait_for_error(r.json()['_id']) as job:
        assert [ts['status'] for ts in job['timestamps']] == \
            [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.ERROR]

        assert job['log'][0].startswith('Exception: Intentionally failed after 0.5 seconds')