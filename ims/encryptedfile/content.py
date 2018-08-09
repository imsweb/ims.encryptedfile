from plone.app.contenttypes.content import File
from zope.interface import implementer, implements

from .interfaces import IEncryptedFile, IEncryptedFileEdit, IEncryptedFileAdd


@implementer(IEncryptedFile)
class EncryptedFile(File):
    """ password-protected """
    implements(IEncryptedFileEdit, IEncryptedFileAdd)
    multiple = False
