# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.size.interfaces import ISized
from dolmen.container.interfaces import IContainer
from dolmen.container.size import ContainerSized


class DummyContainer(object):
    implements(IContainer)

    def __init__(self, numitems):
        self._numitems = numitems

    def __len__(self):
        return self._numitems


def testImplementsISized():
    sized = ContainerSized(DummyContainer(23))
    assert ISized.providedBy(sized)


def testEmptyContainer():
    obj = DummyContainer(0)
    sized = ContainerSized(obj)
    assert sized.sizeForSorting() == ('item', 0)
    assert sized.sizeForDisplay() == u'${items} items'
    assert sized.sizeForDisplay().mapping['items'] == '0'


def testOneItem():
    obj = DummyContainer(1)
    sized = ContainerSized(obj)
    assert sized.sizeForSorting() == ('item', 1)
    assert sized.sizeForDisplay() == u'1 item'


def testSeveralItems():
    obj = DummyContainer(2)
    sized = ContainerSized(obj)
    assert sized.sizeForSorting() == ('item', 2)
    assert sized.sizeForDisplay() == u'${items} items'
    assert sized.sizeForDisplay().mapping['items'] == '2'
