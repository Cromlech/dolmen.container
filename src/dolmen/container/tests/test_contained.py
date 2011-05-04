# -*- coding: utf-8 -*-

import pickle
import pytest
import zope.interface

from persistent import Persistent
from zope.location.interfaces import ILocation, IContained
from dolmen.container.contained import ContainedProxy


class MyOb(Persistent):
    pass


def test_basic_proxy_attribute_management_and_picklability():
    """Contained-object proxy

    This is a picklable proxy that can be put around objects that
    don't implement IContained.
    """
    l = [1, 2, 3]
    p = ContainedProxy(l)
    p.__parent__ = 'Dad'
    p.__name__ = 'p'

    assert p == [1, 2, 3]
    assert p.__parent__ == 'Dad'
    assert p.__name__ == 'p'
    'p'

    with pytest.raises(TypeError):
        # A proxy is not pickable.
        pickle.loads(pickle.dumps(p))


def test_declarations_on_ContainedProxy():
    """It is possible to make declarations on ContainedProxy objects.
    """

    class I1(zope.interface.Interface):
        pass

    class C(object):
        zope.interface.implements(I1)

    c = C()
    p = ContainedProxy(c)

    assert len(tuple(zope.interface.providedBy(ContainedProxy))) == 0
    assert tuple(zope.interface.implementedBy(ContainedProxy)) == (
        (IContained, ILocation))

    #A proxied object has IContainer, in addition to what the unproxied
    # object has
    assert tuple(zope.interface.providedBy(p)) == (
      (I1, IContained, ILocation))

    class I2(zope.interface.Interface):
        pass

    zope.interface.directlyProvides(c, I2)

    assert tuple(zope.interface.providedBy(p)) == (
      (I2, I1, IContained, ILocation))

    # We can declare interfaces through the proxy
    class I3(zope.interface.Interface):
        pass

    zope.interface.directlyProvides(p, I3)

    assert tuple(zope.interface.providedBy(p)) == (
      (I3, I1, IContained, ILocation))


def test_ContainedProxy_instances_have_no_instance_dictionaries():
    """Make sure that proxies do'nt have dictionnaries.
    """
    class C(object):
        pass

    c = C()
    c.x = 1
    assert c.__dict__ == {'x': 1}

    p = ContainedProxy(c)
    assert p.__dict__ == {}

    p.y = 3
    assert p.__dict__ == {}
