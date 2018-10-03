import base
import os
from ..interfaces import IEncryptionUtility
from zope.component import getUtility
from plone.namedfile.file import NamedFile
from plone import api



base_path = os.path.dirname(os.path.realpath(__file__))


class TestEncrypt(base.IntegrationTestCase):

    def test_encrypt_7z(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        file_format = u'7z'
        password = u'testpass'
        blob = util.encrypt(file_data, file_format, file_name, password)
        #checking the type
        self.assertIsInstance(blob, NamedFile)

    def test_decrypt_7z(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        file_format = u'7z'
        password = u'testpass'
        blob = util.encrypt(file_data, file_format, file_name, password)
        d_file_data, d_file_name = util.decrypt(blob, password)
        #comparing the decrypted file data to what was actually written in the file
        self.assertEqual(d_file_data, "File to be encrypted.")
        self.assertEqual(d_file_name, file_name)

    def test_encrypt_zip(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        file_format = u'7z'
        password = u'testpass'
        blob = util.encrypt(file_data, file_format, file_name, password)
        #checking the type
        self.assertIsInstance(blob, NamedFile)

    def test_decrypt_zip(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        file_format = u'zip'
        password = u'testpass'
        blob = util.encrypt(file_data, file_format, file_name, password)
        d_file_data, d_file_name = util.decrypt(blob, password)
        #comparing the decrypted file data to what was actually written in the file
        self.assertEqual(d_file_data, "File to be encrypted.")
        self.assertEqual(d_file_name, file_name)

    def test_encrypt_folder_multiple(self):
        util = getUtility(IEncryptionUtility)
        portal = api.portal.get()
        obj1 = api.content.create(
            type='File',
            title='Test document 1',
            container=portal)
        obj2 = api.content.create(
            type='Image',
            title='Test document 2',
            container=portal)
        obj3 = api.content.create(
            type='File',
            title='Test document 3',
            container=portal)

        file_format = u'7z'
        password = u'testpass'
        blob = util.encrypt_folder_multiple(portal, file_format, password)
        self.assertIsInstance(blob, NamedFile)


    def test_encrypt_folder_single(self):
        util = getUtility(IEncryptionUtility)
        portal = api.portal.get()
        obj1 = api.content.create(
            type='File',
            title='Test document 1',
            container=portal)
        obj2 = api.content.create(
            type='Image',
            title='Test document 2',
            container=portal)
        file_format = u'zip'
        password = u'testpass'
        blob = util.encrypt_folder_single(portal, file_format, password)
        self.assertIsInstance(blob, NamedFile)




def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)