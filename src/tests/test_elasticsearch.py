from testing.elasticsearch import ElasticSearchServer
import os
import tempfile
import requests
import pytest


# Set this up and tear it down for every function in this test so that we don't
# accidentally have an elasticsearch server running when we mean to close it
# down.
@pytest.fixture(scope='function')
def elasticsearch(request):
    """
    A testing fixture that utilizes manually starting and stopping the elasticsearch
    server.
    """
    es = ElasticSearchServer()
    es.start()
    request.addfinalizer(es.stop)
    return es


def test_elasticsearch_context():
    """
    Verify that using the elasticsearch server as a context block sets up and
    tears down as expected.
    """
    es = ElasticSearchServer()

    with pytest.raises(requests.exceptions.MissingSchema):
        # invalid uri
        requests.get(es.uri())

    previous_uri = None
    with es as es:
        uri = es.uri()
        result = requests.get(uri)
        assert result.status_code == 200
        assert uri is not None
        previous_uri = uri

    with pytest.raises(requests.exceptions.ConnectionError):
        # elasticsearch is no longer running
        requests.get(previous_uri)


def test_elasticsearch_fixture(elasticsearch):
    """
    Verify that the elasticsearch fixture works as expected in a testing scenario.
    """
    assert elasticsearch.uri() == 'http://%s:%s' % (elasticsearch._bind_host, elasticsearch._bind_port)

    result = requests.get(elasticsearch.uri())
    assert result.status_code == 200


def test_elasticsearch_teardown():
    """
    Verify that temporary directories and files are cleaned up after the server
    is stopped.
    """
    es = ElasticSearchServer()
    with es as es:
        result = requests.get(es.uri())
        assert result.status_code == 200

    assert not os.path.isdir(es._root)


def test_elasticsearch_existing_dir():
    """
    Verify that when specifying an existing root directory, no cleanup actions
    are performed.
    """
    tmp_dir = tempfile.mkdtemp(suffix='-testing-elastic')

    with ElasticSearchServer(root=tmp_dir) as es:
        result = requests.get(es.uri())
        assert result.status_code == 200

    paths = os.listdir(tmp_dir)
    assert 'data' in paths, "elasticsearch data directory should not have been removed."
    assert os.path.isdir(os.path.join(tmp_dir, 'data'))
    assert 'logs' in paths, "elasticsearch logs directory should not have been removed."
    assert os.path.isdir(os.path.join(tmp_dir, 'logs'))
