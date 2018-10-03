import base
import os
from ..interfaces import IEncryptionUtility
from zope.component import getUtility
from plone import api
from plone.namedfile import NamedFile
from ims.encryptedfile.utility import DecryptionError


base_path = os.path.dirname(os.path.realpath(__file__))


class TestEncrypt(base.IntegrationTestCase):

    def test_encrypt(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        password = u'testpass'

        ##7z
        file_format = u'7z'
        blob = util.encrypt(file_data, file_format, file_name, password)
        #checking the type
        self.assertIsInstance(blob, NamedFile)

        ##zip
        file_format = u'zip'
        blob = util.encrypt(file_data, file_format, file_name, password)
        # checking the type
        self.assertIsInstance(blob, NamedFile)

    def test_decrypt(self):
        util = getUtility(IEncryptionUtility)
        file_name = u'file_to_encrypt.txt'
        f = open(os.path.join(base_path, file_name))
        file_data = NamedFile(f.read(), filename=file_name)
        password = u'testpass'

        ##7z
        file_format = u'7z'
        blob = util.encrypt(file_data, file_format, file_name, password)
        d_file_data, d_file_name = util.decrypt(blob, password)
        #comparing the decrypted file data to what was actually written in the file
        self.assertEqual(d_file_data, "File to be encrypted.")
        self.assertEqual(d_file_name, file_name)

        ##zip
        file_format = u'zip'
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
        obj1.file = NamedFile("Text that need encryption", filename=u'testfile.txt')

        obj2 = api.content.create(
            type='File',
            title='Test document 2',
            container=portal)

        obj2.file = NamedFile("To the moon and back", filename=u'testfile2.txt')

        obj3 = api.content.create(
            type='File',
            title='Test document 3',
            container=portal)
        obj3.file = NamedFile("The mars rover.!2", filename=u'testfile3.txt')
        password = u'testpass'

        #7z
        file_format = u'7z'
        blob = util.encrypt_folder_multiple(portal, file_format, password)
        self.assertIsInstance(blob, NamedFile)
        #error testing
        self.assertRaises(DecryptionError, util.decrypt(blob, password))

        # zip
        file_format = u'zip'
        blob = util.encrypt_folder_multiple(portal, file_format, password)
        self.assertIsInstance(blob, NamedFile)
        # error testing
        self.assertRaises(DecryptionError, util.decrypt(blob, password))


    def test_encrypt_folder_single_zip(self):
        util = getUtility(IEncryptionUtility)
        portal = api.portal.get()
        obj1 = api.content.create(
            type='File',
            title='Test document 1',
            container=portal)
        obj1.file = NamedFile("Text that needs encryption", filename=u'testfile.txt')
        password = u'testpass'

        #7z
        file_format = u'7z'
        blob = util.encrypt_folder_single(portal, file_format, password)
        self.assertIsInstance(blob, NamedFile)
        d_file_data, d_file_name = util.decrypt(blob, password)
        # making sure it returns a zip file
        num = len(d_file_name) - 4 #for .zip
        zip = d_file_name[num:]
        self.assertEqual(zip, '.zip')

        #zip
        file_format = u'zip'
        blob = util.encrypt_folder_single(portal, file_format, password)
        self.assertIsInstance(blob, NamedFile)
        d_file_data, d_file_name = util.decrypt(blob, password)
        # making sure it returns a zip file
        num = len(d_file_name) - 4 #for .zip
        zip = d_file_name[num:]
        self.assertEqual(zip, '.zip')

def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)