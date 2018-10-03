from plone.namedfile.field import NamedBlobFile
from plone.supermodel import directives
from plone.supermodel import model
from zope.interface import Interface
from zope.schema import TextLine, Password, Text, Choice, Bool
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from . import _

encryption_formats = SimpleVocabulary([SimpleTerm('7z'), SimpleTerm('zip')])


class IEncryptable(Interface):
    """ marker """


class IEncryptionUtility(Interface):
    def encrypt(self, file_data, format, file_name, password):
        pass

    def decrypt(self, obj, password):
        pass


class IEncryptedFile(model.Schema):
    title = TextLine(
        title=_(u"Title"),
        required=False
    )
    description = Text(
        title=_(u"Description"),
        required=False
    )
    directives.primary('file')
    file = NamedBlobFile(
        title=_(u"File"),
        required=True,
    )


class IEncryptedFileAdd(model.Schema):
    title = TextLine(
        title=_(u"Title"),
        required=False
    )
    description = Text(
        title=_(u"Description"),
        required=False
    )
    file = NamedBlobFile(
        title=_(u"File"),
        required=True,
    )
    format = Choice(
        title=_(u'File format'),
        description=_(u'All formats use the AES-256 encryption method. They can be read with any tool able to decrypt '
                      u'AES encrypted data such as 7-zip or WinZip.'),
        vocabulary=encryption_formats,
        required=True
    )
    password = Password(
        title=_(u"Password"),
        description=_(u"Be sure to store your password somewhere secure. Your password will not be stored on the site "
                      u"and cannot be recovered."),
        required=True,
        default=None,
    )
    password_ctl = Password(
        title=_(u"Confirm Password"),
        description=_(u"Re-enter the password"),
        required=True,
        default=None,
    )


class IEncryptedFileEdit(model.Schema):
    title = TextLine(
        title=_(u"Title"),
        required=False
    )
    description = Text(
        title=_(u"Description"),
        required=False
    )


class IEncryptPlainFile(model.Schema):
    format = Choice(
        title=_(u'File format'),
        description=_(u'All formats use the AES-256 encryption method. They can be read with any tool able to decrypt '
                      u'AES encrypted data such as 7-zip or WinZip.'),
        vocabulary=encryption_formats,
        required=True
    )
    password = Password(
        title=_(u"Password"),
        description=_(u"Be sure to store your password somewhere secure. Your password will not be stored on the site "
                      u"and cannot be recovered."),
        required=True,
        default=None,
    )
    password_ctl = Password(
        title=_(u"Confirm Password"),
        description=_(u"Re-enter the password"),
        required=True,
        default=None,
    )


class IDecryptFile(model.Schema):
    password = Password(
        title=_(u"Password"),
        description=_(u"Enter the password provided by the file owner."),
        required=True,
        default=None,
    )
