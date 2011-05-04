# -*- coding: utf-8 -*-

import pytest
import zope.component
import zope.interface
from dolmen.container.components import Container
from dolmen.container.interfaces import IContainer
from dolmen.container.contained import (
    NameChooser, NameReserved, IReservedNames)


def test_checkName():
    container = Container()
    container['foo'] = 'bar'
    checkName = NameChooser(container).checkName

    # invalid type for the name
    with pytest.raises(TypeError):
        checkName(2, object())
        checkName([], object())
        checkName(None, object())
        checkName(None, None)

    # invalid names
    with pytest.raises(ValueError):
        checkName('+foo', object())
        checkName('@foo', object())
        checkName('f/oo', object())
        checkName('', object())

    # existing names
    with pytest.raises(KeyError):
        checkName('foo', object())
        checkName(u'foo', object())

    # correct names
    assert checkName('2', object())
    assert checkName(u'2', object())
    assert checkName('other', object())
    assert checkName(u'reserved', object())
    assert checkName(u'r\xe9served', object())

    # reserved names
    class ReservedNames(object):
        zope.component.adapts(IContainer)
        zope.interface.implements(IReservedNames)

        def __init__(self, context):
            self.reservedNames = set(('reserved', 'other'))

    zope.component.provideAdapter(ReservedNames)

    with pytest.raises(NameReserved):
        checkName('reserved', object())
        checkName('other', object())
        checkName(u'reserved', object())
        checkName(u'other', object())


def test_chooseName():
    container = Container()
    container['foo.old.rst'] = 'rst doc'
    nc = NameChooser(container)

    # correct name without changes
    assert nc.chooseName('foobar.rst', None) == u'foobar.rst'
    assert nc.chooseName(u'\xe9', None) == u'\xe9'

    # automatically modified named
    assert nc.chooseName('foo.old.rst', None) == u'foo.old-2.rst'
    assert nc.chooseName('+@+@foo.old.rst', None) == u'foo.old-2.rst'
    assert nc.chooseName('+@+@foo/foo+@', None) == u'foo-foo+@'

    # empty name
    assert nc.chooseName('', None) == u'NoneType'
    assert nc.chooseName('@+@', []) == u'list'

    # if the name is not a string it is converted
    assert nc.chooseName(None, None) == u'None'
    assert nc.chooseName(2, None) == u'2'
    assert nc.chooseName([], None) == u'[]'

    container['None'] = 'something'
    assert nc.chooseName(None, None) == u'None-2'

    container['None-2'] = 'something'
    assert nc.chooseName(None, None) == u'None-3'

    # even if the given name cannot be converted to unicode
    class BadBoy:
        def __unicode__(self):
            raise Exception

    assert nc.chooseName(BadBoy(), set()) == u'set'
