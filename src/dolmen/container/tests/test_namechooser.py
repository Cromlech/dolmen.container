# -*- coding: utf-8 -*-

import pytest
import zope.component
import zope.interface
from zope.location.interfaces import IContained
from dolmen.container.components import Container
from dolmen.container.interfaces import IContainer
from dolmen.container.contained import NameChooser, NameReserved, IReservedNames


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
