# -*- coding: utf-8 -*-

import pytest
import zope.component
from zope.testing.cleanup import cleanUp
from dolmen.container.components import OrderedBTreeContainer
from zope.component.eventtesting import getEvents, clearEvents
from zope.component.testing import PlacelessSetup as CAPlacelessSetup
from zope.component.eventtesting import PlacelessSetup as EventPlacelessSetup
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectModifiedEvent)


def setup_module(module):
    CAPlacelessSetup().setUp()
    EventPlacelessSetup().setUp()


def teardown_module(module):
    clearEvents()
    cleanUp()


def test_order_events():
    oc = OrderedBTreeContainer()

    oc['foo'] = 'bar'
    oc['baz'] = 'quux'
    oc['zork'] = 'grue'

    assert oc.keys() == ['foo', 'baz', 'zork']

    clearEvents()
    oc.updateOrder(['baz', 'foo', 'zork'])
    assert oc.keys() == ['baz', 'foo', 'zork']

    events = getEvents()
    assert [event.__class__.__name__ for event in events] == (
        ['ContainerModifiedEvent'])

    assert IObjectModifiedEvent.providedBy(events[0])


def test_all_items_available_at_object_added_event():

    keys = {}

    @zope.component.adapter(IObjectAddedEvent)
    def containerKeys(event):
        keys[event.object] = event.newParent.keys()

    zope.component.provideHandler(containerKeys)
    oc = OrderedBTreeContainer()
    oc['foo'] = 'FOO'
    assert keys['FOO'] == oc.keys() == ['foo']


def test_exception_causes_order_fix():

    @zope.component.adapter(IObjectAddedEvent)
    def raiseException(event):
        raise RuntimeError()

    zope.component.provideHandler(raiseException)

    oc = OrderedBTreeContainer()
    with pytest.raises(RuntimeError):
        oc['foo'] = 'FOO'

    assert not 'foo' in oc.keys()
