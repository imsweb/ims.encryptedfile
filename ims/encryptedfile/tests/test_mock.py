import base


class MockTest(base.UnitTestCase):
    def test_true(self):
        self.assertTrue(True)

    def test_false(self):
        self.assertFalse(True)


def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
