testing.elasticsearch
=====================

`testing.elasticsearch` automatically sets up an elasticsearch instance in a
temporary directory, and destroys it after testing. It's useful as a pytest
fixture for testing interactions with elasticsearch in an isolated manner.


Implementation is based off the awesome `testing.redis<https://bitbucket.org/tk0miya/testing.redis>`_ module.

Example usage:

    import testing.elasticsearch
    import pyes.es import ES

    # launch new elasticsearch server:
    with testing.elasticsearch.ElasticSearchServer() es:
        elasticsearch = ES(es.dsn())
        # perform any testing with elasticsearch here

    # elasticsearch server is terminated and cleaned up here
