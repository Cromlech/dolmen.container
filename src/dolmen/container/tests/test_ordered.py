# -*- coding: utf-8 -*-

import pytest
from dolmen.container.components import OrderedBTreeContainer
from zope.event import subscribers as event_subscribers
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent import ObjectAddedEvent
from cromlech.container.contained import ContainerModifiedEvent


events = []

def getEvents(event_type=None, filter=None):
    return events


def clearEvents():
    del events[:]


def setup_module(module):
    event_subscribers.append(events.append)


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
    clearEvents()
    

def test_all_items_available_at_object_added_event():

    oc = OrderedBTreeContainer()
    oc['foo'] = 'FOO'

    events = getEvents()
    assert isinstance(events[0], ObjectAddedEvent)
    assert isinstance(events[1], ContainerModifiedEvent)    
    assert events[0].newParent.keys() == oc.keys() == ['foo']
