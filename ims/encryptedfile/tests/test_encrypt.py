import base
import os
from ..interfaces import IEncryptionUtility
from zope.component import getUtility
from plone.namedfile.file import NamedFile


base_path = os.path.dirname(os.path.realpath(__file__))


class TestEncrypt(base.IntegrationTestCase):

    def test_encrypt(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        file_format = u'txt'
        password = u'testpass'
        blob = util.encrypt(file_data, file_format, file_name, password)
        self.assertIsInstance(NamedFile, blob)



def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)