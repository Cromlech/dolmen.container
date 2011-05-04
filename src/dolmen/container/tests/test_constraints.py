# -*- coding: utf-8 -*-
"""Containment constraints

Containment constraints allow us to express restrictions on the types
of items that can be placed in containers or on the types of
containers an item can be placed in.  We express these constraints in
interfaces.
"""

import pytest
from dolmen.container.components import Container
from dolmen.container.constraints import checkObject, checkFactory
from dolmen.container.constraints import containers, contains
from dolmen.container.interfaces import IContainer
from dolmen.container.interfaces import InvalidContainerType, InvalidItemType
from zope import interface
from zope.component.factory import Factory
from zope.location.interfaces import IContained, ILocation


class IBuddyFolder(IContainer):
    """In this example, we will use the contains function to declare
    that objects that provide IBuddyFolder can only contain items that
    provide IBuddy. Note that we use a string containing a dotted name
    for the IBuddy interface. This is because IBuddy hasn't been defined
    yet.  When we define IBuddy, we can use IBuddyFolder directly.
    """
    contains('.IBuddy')


class IBuddy(IContained):
    containers(IBuddyFolder)


def test_contraints():

    class Buddy:
        interface.implements(IBuddy)

    class BuddyFolder:
        interface.implements(IBuddyFolder)

    assert checkObject(BuddyFolder(), 'x', Buddy()) is None
    assert checkFactory(BuddyFolder(), 'x', Factory(Buddy))

    class Contained:
        interface.implements(IContained)

    with pytest.raises(InvalidContainerType):
        checkObject(Container(), 'x', Buddy())

    assert not checkFactory(Container(), 'x', Factory(Buddy))

    with pytest.raises(InvalidItemType):
        checkObject(BuddyFolder(), 'x', Contained())


class IContact(IContained):
    containers('.IContacts')


class IContacts(IContainer):
    contains(IContact)


def test_constraints_order():
    """In the previous tests, we defined the container first and
    then the items.  We can define these in the opposite order.
    """
    class Contact:
        interface.implements(IContact)

    class Contacts:
        interface.implements(IContacts)

    assert checkObject(Contacts(), 'x', Contact()) is None
    assert checkFactory(Contacts(), 'x', Factory(Contact))

    with pytest.raises(InvalidItemType):
        checkObject(Contacts(), 'x', object())

    assert not checkFactory(Contacts(), 'x', Factory(object))


def test_moving_failure():
    """The constraints prevent us from moving a container beneath
    itself (either into itself or another folder beneath it).
    """
    container = Container()

    with pytest.raises(TypeError):
        checkObject(container, 'x', container)

    subcontainer = Container()
    interface.directlyProvides(subcontainer, ILocation)
    subcontainer.__parent__ = container

    with pytest.raises(TypeError):
        checkObject(subcontainer, 'x', container)
