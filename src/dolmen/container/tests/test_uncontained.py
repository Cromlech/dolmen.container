# -*- coding: utf-8 -*-
"""Clear the containment relationship between the `object` and
the `container`.
"""

from dolmen.container.contained import Contained, containedEvent, uncontained
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.testing.cleanup import cleanUp
from zope.component.eventtesting import getEvents, clearEvents
from zope.component.testing import PlacelessSetup as CAPlacelessSetup
from zope.component.eventtesting import PlacelessSetup as EventPlacelessSetup


def setup_module(module):
    CAPlacelessSetup().setUp()
    EventPlacelessSetup().setUp()


def teardown_module(module):
    clearEvents()
    cleanUp()


class Item(Contained):
    pass


def test_uncontained():
    item = Item()
    container = {u'foo': item}
    x, event = containedEvent(item, container, u'foo')

    assert item.__parent__ is container
    assert item.__name__ == u'foo'

    uncontained(item, container, u'foo')
    assert item.__parent__ is None
    assert item.__name__ is None

    assert len(getEvents(IObjectRemovedEvent)) == 1

    event = getEvents(IObjectRemovedEvent)[-1]
    assert event.object is item
    assert event.oldParent is container
    assert event.oldName == u'foo'
    assert event.newParent is None
    assert event.newName is None

    assert len(getEvents(IObjectModifiedEvent)) == 1
    assert getEvents(IObjectModifiedEvent)[-1].object is container

    # Events are never triggered twice
    uncontained(item, container, u'foo')
    assert len(getEvents(IObjectRemovedEvent)) == 1
    assert len(getEvents(IObjectModifiedEvent)) == 1

    item.__parent__, item.__name__ = container, None
    uncontained(item, container, u'foo')
    assert len(getEvents(IObjectRemovedEvent)) == 1
    assert len(getEvents(IObjectModifiedEvent)) == 2

    item.__parent__, item.__name__ = None, u'bar'
    uncontained(item, container, u'foo')
    assert len(getEvents(IObjectRemovedEvent)) == 1
    assert len(getEvents(IObjectModifiedEvent)) == 3
