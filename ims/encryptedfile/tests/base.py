import unittest

import transaction
from ims.encryptedfile import testing
from plone.app.testing import setRoles, TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser


class UnitTestCase(unittest.TestCase):
    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):
    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer
        setRoles(self.portal, TEST_USER_ID, ['Manager'])


class FunctionalTestCase(IntegrationTestCase):
    layer = testing.FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        transaction.commit()
