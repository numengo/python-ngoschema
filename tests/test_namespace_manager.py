import pytest

from future.utils import with_metaclass
from ngoschema.exceptions import InvalidValue

from ngoschema.managers import NamespaceManager


def test_namespace_manager():
    ns_mgr = NamespaceManager()
    uri = 'https://numengo.org/ngoschema/document#/$defs/Document'
    assert ns_mgr.get_cname_id('ngoschema.document.Document') == uri
    assert ns_mgr.get_id_cname(uri) == 'ngoschema.document.Document', ns_mgr.get_id_cname(uri)
    ns_mgr2 = NamespaceManager(document='https://numengo.org/ngoschema/document')
    assert ns_mgr2.get_id_cname(uri) == 'document.Document'
    assert ns_mgr2.load('document.Document')
    return


if __name__ == '__main__':
    test_namespace_manager()
