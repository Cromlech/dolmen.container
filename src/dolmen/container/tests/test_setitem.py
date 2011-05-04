# -*- coding: utf-8 -*-

"""Helper function to set an item and generate needed events

This helper is needed, in part, because the events need to get
published after the `object` has been added to the `container`.
"""

import pytest
import zope.component

from zope.location import Location
from zope.location.interfaces import IContained
from zope.interface import Interface, implements
from zope.testing.cleanup import cleanUp
from zope.component.eventtesting import setUp, getEvents, clearEvents
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectMovedEvent, IObjectModifiedEvent)

from dolmen.container.contained import setitem
from dolmen.container.components import Contained


class IItem(Interface):
    pass


class Item(Contained):
    implements(IItem)

    def setAdded(self, event):
        self.added = event

    def setMoved(self, event):
        self.moved = event


def added(obj, event):
    obj.setAdded(event)


def moved(obj, event):
    obj.setMoved(event)


def setup_module(module):
    setUp()
    zope.component.provideHandler(added, [IItem, IObjectAddedEvent])
    zope.component.provideHandler(moved, [IItem, IObjectMovedEvent])


def teardown_module(module):
    cleanUp()


def test_setitem():

    item = Item()
    container = {}

    setitem(container, container.__setitem__, u'c', item)
    assert container[u'c'] is item
    assert item.__parent__ is container
    assert item.__name__ == u'c'

    # We should get events
    assert len(getEvents(IObjectAddedEvent)) == 1

    event = getEvents(IObjectAddedEvent)[-1]
    assert event.object is item
    assert event.newParent is container
    assert event.newName == u'c'
    assert event.oldParent is None
    assert event.oldName is None

    # As well as a modification event for the container
    assert len(getEvents(IObjectModifiedEvent)) == 1
    assert getEvents(IObjectModifiedEvent)[-1].object is container

    # The item's hooks have been called:
    assert item.added is event
    assert item.moved is event

    # we clean our test.
    clearEvents()


def test_no_event():
    """We can suppress events and hooks by setting the `__parent__` and
    `__name__` first
    """
    item = Item()
    container = {}

    # By setting the __parent__ and __name, we act as if we were
    # already contained.
    item.__parent__, item.__name__ = container, 'c'
    setitem(container, container.__setitem__, u'c', item)

    assert len(container) == 1
    assert len(getEvents(IObjectAddedEvent)) == 0
    assert len(getEvents(IObjectModifiedEvent)) == 0

    assert getattr(item, 'added', None) is None
    assert getattr(item, 'moved', None) is None

    # we clean our test.
    clearEvents()


def test_move_event():
    """If the item had a parent or name (as in a move or rename),
    we generate a move event, rather than an add event.
    """
    container = {}

    # We create a first item
    item = Item()
    setitem(container, container.__setitem__, u'c1', item)

    # Add operation are "moved" events.
    assert len(getEvents(IObjectMovedEvent)) == 1

    # We created an item already contained.
    item = Item()
    item.__parent__, item.__name__ = container, 'c2'
    setitem(container, container.__setitem__, u'c2', item)

    assert len(container) == 2
    assert len(getEvents(IObjectAddedEvent)) == 1
    assert len(getEvents(IObjectModifiedEvent)) == 1
    assert len(getEvents(IObjectMovedEvent)) == 1

    # We now rewrite 'c2' under another name
    # Thus, we created a move event : +1 modification +1 move.
    setitem(container, container.__setitem__, u'c3', item)

    assert len(container) == 3
    assert len(getEvents(IObjectAddedEvent)) == 1
    assert len(getEvents(IObjectModifiedEvent)) == 2
    assert len(getEvents(IObjectMovedEvent)) == 2

    # We also get the move hook called, but not the add hook:
    event = getEvents(IObjectMovedEvent)[-1]
    assert getattr(item, 'added', None) is None
    assert item.moved is event

    # we clean our test.
    clearEvents()


def test_replace():
    """If we try to replace an item without deleting it first, we'll get
    an error.
    """
    container = {}

    # We create a first item
    item = Item()
    setitem(container, container.__setitem__, u'c', item)

    # We try to override
    with pytest.raises(KeyError):
        setitem(container, container.__setitem__, u'c', [])

    # We have to delete to replace a key
    del container[u'c']
    setitem(container, container.__setitem__, u'c', [])

    assert len(getEvents(IObjectAddedEvent)) == 2
    assert len(getEvents(IObjectModifiedEvent)) == 2

    # we clean our test.
    clearEvents()
    

def test_interface_providing():
    """If the object implements `ILocation`, but not `IContained`, set it's
    `__parent__` and `__name__` attributes *and* declare that it
    implements `IContained`.
    """
    container = {}

    item = Location()
    assert not IContained.providedBy(item)

    setitem(container, container.__setitem__, u'l', item)
    assert container[u'l'] is item
    assert item.__parent__ is container
    assert item.__name__ == u'l'
    assert IContained.providedBy(item)

    # We get added and modification events:
    assert len(getEvents(IObjectAddedEvent)) == 1
    assert len(getEvents(IObjectModifiedEvent)) == 1

    # If the object doesn't even implement `ILocation`, put a
    # `ContainedProxy` around it:
    item = []
    setitem(container, container.__setitem__, u'i', item)
    assert container[u'i'] == []
    assert not container[u'i'] is item

    item = container[u'i']
    assert item.__parent__ is container
    assert item.__name__ == u'i'

    assert IContained.providedBy(item)
    assert len(getEvents(IObjectAddedEvent)) == 2
    assert len(getEvents(IObjectModifiedEvent)) == 2

    # we clean our test.
    clearEvents()


def test_key_integrity():
    """We'll get type errors if we give keys that aren't
    unicode or ascii keys:
    """
    container = {}
    item = Item()

    with pytest.raises(TypeError):
        setitem(container, container.__setitem__, 42, item)
        setitem(container, container.__setitem__, None, item)
        setitem(container, container.__setitem__, 'hello ' + chr(200), item)

    with pytest.raises(ValueError):
        setitem(container, container.__setitem__, '', item)
        setitem(container, container.__setitem__, u'', item)
