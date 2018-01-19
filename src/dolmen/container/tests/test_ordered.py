# -*- coding: utf-8 -*-

import pytest
from crom import testing

import crom
import cromlech.events
from cromlech.events import setup_dispatcher, teardown_dispatcher
from dolmen.container.components import OrderedBTreeContainer
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.interface import Interface


def setup_module(module):
    testing.setup()
    crom.configure(cromlech.events)
    setup_dispatcher()


def teardown_module(module):
    testing.teardown()
    teardown_dispatcher()


def test_order_events(events):
    oc = OrderedBTreeContainer()

    oc['foo'] = 'bar'
    oc['baz'] = 'quux'
    oc['zork'] = 'grue'

    assert oc.keys() == ['foo', 'baz', 'zork']

    events.clear()
    oc.updateOrder(['baz', 'foo', 'zork'])
    assert oc.keys() == ['baz', 'foo', 'zork']

    assert [event.__class__.__name__ for event in events] == [
        'ContainerModifiedEvent',
    ]

    assert IObjectModifiedEvent.providedBy(events.pop())


def test_all_items_available_at_object_added_event():

    keys = {}

    def containerKeys(obj, event):
        keys[obj] = event.newParent.keys()

    crom.implicit.registry.subscribe(
        (Interface, IObjectAddedEvent),
        cromlech.events.IEventHandler, containerKeys)

    oc = OrderedBTreeContainer()
    oc['foo'] = 'FOO'
    assert keys['FOO'] == oc.keys() == ['foo']


def test_exception_causes_order_fix():

    def raiseException(obj, event):
        raise RuntimeError()

    crom.implicit.registry.subscribe(
        (Interface, IObjectAddedEvent),
        cromlech.events.IEventHandler, raiseException)

    oc = OrderedBTreeContainer()
    with pytest.raises(RuntimeError):
        oc['foo'] = 'FOO'

    assert not 'foo' in oc.keys()
