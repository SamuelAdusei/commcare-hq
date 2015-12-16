from django.conf import settings

from corehq.util.test_utils import unit_testing_only

TEST_ES_PREFIX = 'test_'


def es_index(index):
    prefix = '' if not settings.UNIT_TESTING else TEST_ES_PREFIX
    return "{}{}".format(prefix, index)


@unit_testing_only
def delete_es_index(es_index):
    from corehq.elastic import get_es_new

    if es_index.startswith(TEST_ES_PREFIX):
        es = get_es_new()
        es.indices.delete(index=es_index)
    else:
        raise DeleteProductionESIndex('You cannot delete a production index in tests!!')


class DeleteProductionESIndex(Exception):
    pass
