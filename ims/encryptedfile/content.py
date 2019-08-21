from plone.app.contenttypes.content import File
from zope.interface import implementer

from .interfaces import IEncryptedFile, IEncryptedFileEdit, IEncryptedFileAdd


@implementer(IEncryptedFile, IEncryptedFileEdit, IEncryptedFileAdd)
class EncryptedFile(File):
    """ password-protected """
    multiple = False
