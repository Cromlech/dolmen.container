# -*- coding: utf-8 -*-
"""Get the sublocations for a container.
"""

from zope.location.interfaces import ISublocations
from zope.interface.verify import verifyObject, verifyClass
from dolmen.container.contained import ContainerSublocations


class MyContainer(object):

    def __init__(self, **data):
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]


def test_sublocations():
    assert verifyClass(ISublocations, ContainerSublocations)

    container = MyContainer(x=1, y=2, z=42)
    adapter = ContainerSublocations(container)
    assert verifyObject(ISublocations, adapter)

    sublocations = list(adapter.sublocations())
    sublocations.sort()
    assert sublocations == [1, 2, 42]
