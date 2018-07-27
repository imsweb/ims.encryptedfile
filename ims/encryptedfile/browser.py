import os
import shutil
import subprocess
import tempfile

from plone import api
from plone.app.contenttypes.browser.file import FileView
from plone.dexterity.browser import add, edit
from plone.namedfile.file import NamedFile
from z3c.form import button
from z3c.form.action import ActionErrorOccurred
from z3c.form.interfaces import WidgetActionExecutionError
from zope.event import notify
from zope.interface import Invalid

from . import _
from .interfaces import IEncryptedFileEdit, IEncryptedFileAdd


class EncryptedFileView(FileView):
    """ view """


class EncryptedFileEditForm(edit.DefaultEditForm):
    schema = IEncryptedFileEdit


class EncryptedFileAddForm(add.DefaultAddForm):
    portal_type = 'EncryptedFile'
    schema = IEncryptedFileAdd

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        # Skip this check if password fields already have an error
        error_keys = [error.field.getName() for error in action.form.widgets.errors]
        if not ('password' in error_keys or 'password_ctl' in error_keys):
            password = data.get('password')
            password_ctl = data.get('password_ctl')
            if password != password_ctl:
                err_str = _(u'Passwords do not match.')
                notify(ActionErrorOccurred(action, WidgetActionExecutionError('password', Invalid(err_str))))
                notify(ActionErrorOccurred(action, WidgetActionExecutionError('password_ctl', Invalid(err_str))))

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
        binary = '7za'
        if os.name == 'nt':
            binary = '7z.exe'

        temp_dir = tempfile.mkdtemp()
        # don't call tempfile.NamedTemporaryFile because we want to preserve filename
        temp = open(os.path.join(temp_dir, data['file'].filename), mode='w+b')
        temp.write(data['file'].data)
        temp.close()

        # 7z format should be AES256 by default, with the -mem flag only needed for .zip,
        # see https://sourceforge.net/p/sevenzip/discussion/45797/thread/bdc0378e/
        # We could download this as a zip and use the -mem flag, but windows compressed file app does not know how to
        # open it Using .7z allows the file to be more easily associated with something that can actually read it (7zip)
        suffix = '.{}'.format(data['format'])
        archive_name = tempfile.mktemp(suffix=suffix, dir=temp_dir)
        if data['format'] == '7z':
            command = [binary, 'a', archive_name, temp.name, '-t7z', '-p{}'.format(data['password'])]
        else:
            command = [binary, 'a', archive_name, temp.name, '-p{}'.format(data['password']), '-mem=AES256']
        subprocess.call(command, stdout=subprocess.PIPE)
        with open(archive_name, 'rb') as archive:
            encrypted = archive.read()
            file_name, file_ext = os.path.splitext(content.file.filename)
            file_name = u'{}.{}'.format(file_name, data['format'])
            content.file = NamedFile(encrypted, filename=file_name)

        content.password = None
        content.password_ctl = None

        shutil.rmtree(temp_dir)
        return content


class EncryptedFileAddView(add.DefaultAddView):
    form = EncryptedFileAddForm
