import os
import shutil
import subprocess
import tempfile
import zipfile

import plone.api as api
from plone.namedfile.file import NamedFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.interface.declarations import implementer_only

from .interfaces import IEncryptionUtility, IEncryptable

try:
    WindowsError
except NameError:
    WindowsError = None


class DecryptionError(Exception):
    """ Could not decrypt """


class Windows7ZipError(Exception):
    """ Exception running 7zip in Windows """


@implementer_only(IEncryptionUtility)
class EncryptionUtility(object):

    @staticmethod
    def binary():
        _binary = '7za'
        if os.name == 'nt':
            _binary = '7z.exe'
        return _binary

    def encrypt(self, file_data, file_format, file_name, password):
        """ encrypt a file with a password. AES256 encoding

        7z format should be AES256 by default, with the -mem flag only needed for .zip,
        see https://sourceforge.net/p/sevenzip/discussion/45797/thread/bdc0378e/
        We could have users download this as a zip and use the -mem flag, but windows compressed file app does not know
        how to open it. Using 7z allows the file to be more easily associated with something that can actually read
        it (7zip)

        :param file_data: NamedFile unencrypted
        :param file_format: 7z, zip, etc
        :param file_name: file name
        :param password: password to encrypt with
        :return: encrypted NamedFile
        """
        temp_dir = tempfile.mkdtemp()
        # don't call tempfile.NamedTemporaryFile because we want to preserve filename
        temp = open(os.path.join(temp_dir, file_data.filename), mode='w+b')
        temp.write(file_data.data)
        temp.close()

        suffix = '.{}'.format(file_format)
        archive_name = tempfile.mktemp(suffix=suffix, dir=temp_dir)
        if file_format == '7z':
            command = [self.binary(), 'a', archive_name, temp.name, '-t7z', '-p{}'.format(password)]
        else:
            command = [self.binary(), 'a', archive_name, temp.name, '-p{}'.format(password), '-mem=AES256']
        try:
            subprocess.call(command, stdout=subprocess.PIPE)
        except WindowsError:
            raise Windows7ZipError('Unable to execute 7zip command. Make sure the location of this binary is in '
                                   'the PATH environment variable')
        with open(archive_name, 'rb') as archive:
            encrypted = archive.read()
            file_name = '{}.{}'.format(file_name, file_format)
            file_name = str(file_name.encode('ascii', 'ignore'))
            blob = NamedFile(encrypted, filename=file_name)

        shutil.rmtree(temp_dir)
        return blob

    def decrypt(self, nfile, password):
        """

        :param nfile: NamedFile
        :param password: password
        :return: decrypted file data, decrypted file name
        """

        temp_dir = tempfile.mkdtemp()
        temp = tempfile.NamedTemporaryFile(mode='w+b', dir=temp_dir, delete=False)
        temp.write(nfile.data)
        temp.close()
        command = [self.binary(), 'e', temp.name, '-o{}'.format(temp_dir), '*', '-p{}'.format(password), '-y']
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.stdout.read()
        p.stdout.close()
        p.terminate()

        if b'Everything is Ok' not in result:
            raise DecryptionError('Failed to decrypt. Maybe wrong password')

        contents = [name for name in os.listdir(temp_dir) if name != os.path.split(temp.name)[-1]]
        if not len(contents):
            raise DecryptionError('Could not extract archive, or archive may be empty')
        elif len(contents) > 1:
            raise DecryptionError('This archive contains multiple files')
        else:
            with open(os.path.join(temp_dir, contents[0]), 'rb') as f:
                file_data = f.read()
        shutil.rmtree(temp_dir)
        return file_data, contents[0]

    def encrypt_folder_multiple(self, container, file_format, password):
        """ Encrypt an entire folder into one archive containing multiple files

        :param container: folderish content
        :param file_format: 7z, zip, etc
        :param password: password to encrypt with
        :return: encrypted NamedFile
        """

        suffix = '.{}'.format(file_format)
        temp_dir = tempfile.mkdtemp()
        archive_name = tempfile.mktemp(suffix=suffix, dir=temp_dir)
        for obj in self.get_encryptable(container):
            primary = IPrimaryFieldInfo(obj)
            if primary:
                plain = primary.value
                # don't call tempfile.NamedTemporaryFile because we want to preserve filename
                temp = open(os.path.join(temp_dir, plain.filename), mode='w+b')
                temp.write(plain.data)
                temp.close()

                if file_format == '7z':
                    command = [self.binary(), 'a', archive_name, temp.name, '-t7z', '-p{}'.format(password)]
                else:
                    command = [self.binary(), 'a', archive_name, temp.name, '-p{}'.format(password), '-mem=AES256']
                subprocess.call(command, stdout=subprocess.PIPE)
        with open(archive_name, 'rb') as archive:
            encrypted = archive.read()
            file_name = '{}.{}'.format(container.getId(), file_format)
            file_name = str(file_name.encode('ascii', 'ignore'))
            blob = NamedFile(encrypted, filename=file_name)

        shutil.rmtree(temp_dir)
        return blob

    def encrypt_folder_single(self, container, file_format, password):
        """ Encrypt an entire folder into one archive containing a single zip

        :param container: folderish content
        :param file_format: 7z, zip, etc
        :param password: password to encrypt with
        :return: encrypted NamedFile
        """

        suffix = '.{}'.format(file_format)
        temp_dir = tempfile.mkdtemp()
        archive_name = tempfile.mktemp(suffix=suffix, dir=temp_dir)
        zip_archive_name = os.path.join(temp_dir, container.getId() + '.zip')
        zipper = zipfile.ZipFile(zip_archive_name, 'w', zipfile.ZIP_DEFLATED)
        for obj in self.get_encryptable(container):
            primary = IPrimaryFieldInfo(obj)
            if primary:
                plain = primary.value
                # don't call tempfile.NamedTemporaryFile because we want to preserve filename
                temp = open(os.path.join(temp_dir, plain.filename), mode='w+b')
                temp.write(plain.data)
                temp.close()
                zipper.write(temp.name, os.path.split(temp.name)[-1])
        zipper.close()

        if file_format == '7z':
            command = [self.binary(), 'a', archive_name, zip_archive_name, '-t7z', '-p{}'.format(password)]
        else:
            command = [self.binary(), 'a', archive_name, zip_archive_name, '-p{}'.format(password), '-mem=AES256']
        subprocess.call(command, stdout=subprocess.PIPE)
        with open(archive_name, 'rb') as archive:
            encrypted = archive.read()
            file_name = '{}.{}'.format(container.getId(), file_format)
            file_name = str(file_name.encode('ascii', 'ignore'))
            blob = NamedFile(encrypted, filename=file_name)

        shutil.rmtree(temp_dir)
        return blob

    encrypt_folder = encrypt_folder_single

    def get_encryptable(self, container, brains=False):
        catalog = api.portal.get_tool('portal_catalog')
        query = dict(
            portal_type=[ptype for ptype in catalog.uniqueValuesFor('portal_type') if ptype != 'EncryptedFile'],
            object_provides=IEncryptable.__identifier__,
            path={'query': '/'.join(container.getPhysicalPath()), 'depth': 1}
        )
        if brains:
            return catalog(**query)
        return [brain.getObject() for brain in catalog(**query)]
