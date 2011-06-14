# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
from os.path import join

name = 'dolmen.container'
version = '0.2'
readme = open(join('src', 'dolmen', 'container', "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'ZODB3 >= 3.10',
    'setuptools',
    'zope.interface',
    'cromlech.container',
    ]

tests_require = [
    'pytest',
    'zope.testing',
    'zope.component',
    'zope.lifecycleevent',
    'zope.component [test]',
    ]

setup(name=name,
      version=version,
      description='Dolmen containers components',
      long_description=readme + '\n\n' + history,
      keywords='Dolmen container implementation, using ZODB BTrees.',
      author='The Dolmen team',
      author_email='dolmen@list.dolmen-project.org',
      url='',
      license='ZPL',
      classifiers=[
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['dolmen'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={
          'test': tests_require,
          },
      )
