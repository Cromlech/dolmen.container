# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
from os.path import join

name = 'dolmen.container'
version = '0.1'
readme = open(join('src', 'dolmen', 'container', "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'ZODB3 >= 3.10',
    'setuptools',
    'zope.broken',
    'zope.component',
    'zope.dottedname',
    'zope.event',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.lifecycleevent',
    'zope.location',
    'zope.schema',
    'zope.security',
    ]

tests_require = [
    'pytest',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen containers components',
      long_description = readme + '\n\n' + history,
      keywords = 'Dolmen container implementation, using ZODB BTrees.',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = '',
      license = 'ZPL',
      classifiers = [
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {
          'test': tests_require,
          },
      ext_modules=[
          Extension("dolmen.container._dolmen_container_contained",
                             [os.path.join("src", "dolmen", "container",
                                           "_dolmen_container_contained.c")
                              ], include_dirs=['include']),
                   ],
      )
