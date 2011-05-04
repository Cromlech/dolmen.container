# -*- coding: utf-8 -*-

from zope.location import Location
from zope.location.interfaces import IContained
from dolmen.container.contained import Contained, containedEvent
from zope.testing.cleanup import cleanUp
from zope.component.eventtesting import clearEvents
from zope.component.testing import PlacelessSetup as CAPlacelessSetup
from zope.component.eventtesting import PlacelessSetup as EventPlacelessSetup


def setup_module(module):
    CAPlacelessSetup().setUp()
    EventPlacelessSetup().setUp()


def teardown_module(module):
    clearEvents()
    cleanUp()


def test_contained_event():

    container = {}
    item = Contained()
    x, event = containedEvent(item, container, u'foo')
    assert x is item
    assert item.__parent__ is container
    assert item.__name__ == u'foo'

    assert event.__class__.__name__ == 'ObjectAddedEvent'
    assert event.object is item
    assert event.newParent is container
    assert event.newName == u'foo'
    assert event.oldParent is None
    assert event.oldName is None

    # Event is not triggered twice.
    x2, event = containedEvent(item, container, u'foo')
    assert x2 is item
    assert item.__parent__ is container
    assert item.__name__ == u'foo'

    assert not event

    # Moved event
    x, event = containedEvent(item, container, u'foo2')
    assert event.__class__.__name__ == 'ObjectMovedEvent'
    assert event.object is item
    assert event.newParent is container
    assert event.newName == u'foo2'
    assert event.oldParent is container
    assert event.oldName == u'foo'

    # Ilocation enrichment
    item = Location()
    assert not IContained.providedBy(item)

    x, event = containedEvent(item, container, 'foo')
    assert x is item
    assert item.__parent__ is container
    assert item.__name__ == 'foo'
    assert IContained.providedBy(item)

    # Containment proxy
    item = []
    x, event = containedEvent(item, container, 'foo')
    assert not x is item
    assert x.__parent__ is container
    assert x.__name__ == 'foo'

    # Make sure we don't lose existing directly provided interfaces.
    from zope.interface import Interface, directlyProvides

    class IOther(Interface):
        pass

    item = Location()
    directlyProvides(item, IOther)
    assert IOther.providedBy(item)

    x, event = containedEvent(item, container, 'foo')
    assert IOther.providedBy(item)
