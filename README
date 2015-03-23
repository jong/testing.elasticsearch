testing.elasticsearch
=====================

`testing.elasticsearch` automatically sets up an elasticsearch instance in a
temporary directory, and destroys it after testing. It's useful as a pytest
fixture for testing interactions with elasticsearch in an isolated manner.


Implementation is based off the awesome [testing.redis](https://bitbucket.org/tk0miya/testing.redis) module.

Example usage:


    import testing.elasticsearch
    import pyes.es import ES

    # launch new elasticsearch server:
    with testing.elasticsearch.ElasticSearchServer() es:
        elasticsearch = ES(es.dsn())
        # perform any testing with elasticsearch here

    # elasticsearch server is terminated and cleaned up here


You can also setup a pytest fixture:


    @pytest.fixture(scope='session')
    def elasticsearch(request):
        """
        A testing fixture that provides a running elasticsearch server.
        """
        es = ElasticSearchServer()
        es.start()
        request.addfinalizer(es.stop)
        return es


Testing
-------

To run tests you'll need to install the test requirements:


    pip install -r src/tests/requirements.txt

Run tests:

    python src/tests/runtests.py
