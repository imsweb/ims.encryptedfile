from setuptools import setup, find_packages

version = '2.0.2'

setup(name='ims.encryptedfile',
      version=version,
      description="",
      classifiers=[
          "Framework :: Plone :: 5.2",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Eric Wohnlich',
      author_email='wohnlice@imsweb.com',
      url='https://github.com/imsweb/ims.encryptedfile',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ims'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      extras_require={
          'test': ['plone.app.testing', 'plone.mocktestcase', 'formencode'],
      },

      )
