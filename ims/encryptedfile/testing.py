import ims.encryptedfile
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting, applyProfile, PLONE_FIXTURE


class EncryptedFileSiteLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configuration_context):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=ims.encryptedfile)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ims.encryptedfile:default')


ENCRYPTED_FILE_SITE_FIXTURE = EncryptedFileSiteLayer()

INTEGRATION = IntegrationTesting(
    bases=(ENCRYPTED_FILE_SITE_FIXTURE,),
    name="ims.encryptedfile:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(ENCRYPTED_FILE_SITE_FIXTURE,),
    name="ims.encryptedfile:Functional"
)
