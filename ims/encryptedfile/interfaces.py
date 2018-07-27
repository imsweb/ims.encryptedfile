from plone.supermodel import model
from zope.schema import TextLine, Password, Text, Choice
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import directives
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from . import _

encryption_formats = SimpleVocabulary([SimpleTerm('7z'), SimpleTerm('zip')])


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
        description=_(u'All formats use AES256 encryption'),
        vocabulary=encryption_formats,
        required=True
    )
    password = Password(
        title=_(u"Password"),
        description=_(u"Your password will not be stored on the system and cannot be recovered by it."),
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
