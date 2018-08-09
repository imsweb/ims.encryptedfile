import mimetypes
import os

from Acquisition import aq_inner, aq_parent
from Products.Five import BrowserView
import plone.api as api
from plone.app.contenttypes.browser.file import FileView
from plone.autoform.form import AutoExtensibleForm
from plone.dexterity.browser import add, edit
from plone.rfc822.interfaces import IPrimaryFieldInfo
from z3c.form import button, form
from z3c.form.action import ActionErrorOccurred
from z3c.form.interfaces import WidgetActionExecutionError
from zope.component import getUtility
from zope.event import notify
from plone.dexterity.interfaces import IDexterityContainer
from zope.interface import Invalid
from zope.lifecycleevent import ObjectModifiedEvent

from . import _
from .interfaces import IEncryptedFileEdit, IEncryptedFileAdd, IEncryptPlainFile, IEncryptable, IEncryptedFile, \
    IDecryptFile, IEncryptionUtility
from .utility import DecryptionError


class EncryptedFileView(FileView):
    """ view """


class EncryptedFileEditForm(edit.DefaultEditForm):
    schema = IEncryptedFileEdit


def validate_passwords(action, data):
    # Skip this check if password fields already have an error
    error_keys = [error.field.getName() for error in action.form.widgets.errors]
    if not ('password' in error_keys or 'password_ctl' in error_keys):
        password = data.get('password')
        password_ctl = data.get('password_ctl')
        if password != password_ctl:
            err_str = _(u'Passwords do not match.')
            notify(ActionErrorOccurred(action, WidgetActionExecutionError('password', Invalid(err_str))))
            notify(ActionErrorOccurred(action, WidgetActionExecutionError('password_ctl', Invalid(err_str))))


class EncryptUtils(BrowserView):
    def encrypt_file(self):
        if not IEncryptable.providedBy(self.context):
            return False
        if IEncryptedFile.providedBy(self.context):
            return False
        return True

    def encrypt_folder(self):
        if IDexterityContainer.providedBy(self.context):
            util = getUtility(IEncryptionUtility)
            if util.get_encryptable(self.context, brains=True):
                return True


class EncryptedFileAddForm(add.DefaultAddForm):
    portal_type = 'EncryptedFile'
    schema = IEncryptedFileAdd

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        validate_passwords(action, data)

        if action.form.widgets.errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            api.portal.show_message(self.success_message, self.request, "info")

    def create(self, data):
        """ We perform a one-time operation to password-protect the file as it's uploaded
            The process can be broken down like this
            1. File is uploaded and super() creates the content obj. At this point the transaction has not been
               committed so the file's BLOB data (content.file._blob) exists only as a temp file
            2. Make a temp dir for our workspace
            3. Copy file data to workspace, we're keeping the same file name
            4. Create a temp file name with suffix '.zip'
            5. Run 7z CLI to create archive from temp file to the path in step #4
            6. Remove temp dir and its contents

        :param data: z3c form data extraction
        :return: content object
        """
        content = super(EncryptedFileAddForm, self).create(data)
        file_name = data.get('file_name')
        if not file_name:
            file_name, file_ext = os.path.splitext(content.file.filename)

        util = getUtility(IEncryptionUtility)
        encrypted = util.encrypt(data['file'], data['format'], file_name, data['password'])

        content.password = None
        content.password_ctl = None
        content.file = encrypted
        return content


class EncryptedFileAddView(add.DefaultAddView):
    form = EncryptedFileAddForm


class EncryptPlainFile(AutoExtensibleForm, form.Form):
    label = u'Encrypt File'
    ignoreContext = True
    schema = IEncryptPlainFile
    redirect = False

    def render(self):
        if not self.redirect:
            return super(EncryptPlainFile, self).render()

    @button.buttonAndHandler(u'Encrypt')
    def handle_encrypt(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        validate_passwords(action, data)
        orig = IPrimaryFieldInfo(self.context).value
        container = aq_parent(aq_inner(self.context))
        add_view = EncryptedFileAddForm(container, self.request)
        params = {
            'file': orig,
            'format': data['format'],
            'password': data['password'],
            'id': self.context.id,
            'title': self.context.title,
            'file_name': os.path.splitext(orig.filename)[0]
        }
        encrypted_file = add_view.createAndAdd(params)  # does not have context
        add_view._finishedAdd = True

        api.content.delete(obj=self.context)

        encrypted_file = container[encrypted_file.getId()]

        api.portal.show_message(_(u'File successfully password-protected'), self.request, 'info')
        return self.request.response.redirect(encrypted_file.absolute_url() + '/view')


class DecryptFile(AutoExtensibleForm, form.Form):
    label = u'Decrypt and Download'
    schema = IDecryptFile
    ignoreContext = True
    output = None
    file_name = ''

    def render(self):
        if not self.output:
            return super(DecryptFile, self).render()
        else:
            mime = mimetypes.guess_type(self.file_name)[0] or ""
            self.request.response.setHeader('Content-Type', mime + ' charset=utf-8')
            self.request.response.setHeader('Content-disposition', 'attachment;filename={}'.format(self.file_name))
            return self.output

    @button.buttonAndHandler(_(u'Decrypt'), name='decrypt')
    def handle_decrypt(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        util = getUtility(IEncryptionUtility)
        try:
            plain, file_name = util.decrypt(self.context.file, data['password'])
            self.output = plain
            self.file_name = file_name
        except DecryptionError, e:
            api.portal.show_message(_(e.message), self.request, 'error')


class ZipEncryptFolder(AutoExtensibleForm, form.Form):
    label = u'Zip and Encrypt Folder'
    description = _(u'This will add all Files and Images in this folder into a single password protected zip file.'
                    u' Already encrypted files will be ignored.')
    ignoreContext = True
    schema = IEncryptPlainFile
    redirect = False

    def render(self):
        if not self.redirect:
            return super(ZipEncryptFolder, self).render()

    @button.buttonAndHandler(u'Encrypt')
    def handle_encrypt(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        validate_passwords(action, data)
        utility = getUtility(IEncryptionUtility)
        encrypted = utility.encrypt_folder(self.context, data['format'], data['password'])

        api.content.delete(objects=utility.get_encryptable(self.context))

        archive_id = '{}.{}'.format(self.context.getId(), data['format'])
        api.content.create(container=self.context, id=archive_id, title=archive_id, type='EncryptedFile')
        obj = self.context.restrictedTraverse(archive_id)
        obj.file = encrypted
        notify(ObjectModifiedEvent(self.context))
        self.redirect = True
        api.portal.show_message(_(u'Successfully encrypted folder.'), self.request, 'info')
        self.request.response.redirect(obj.absolute_url()+'/view')
