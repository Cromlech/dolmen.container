# -*- coding: utf-8 -*-
"""Containment constraints

Containment constraints allow us to express restrictions on the types
of items that can be placed in containers or on the types of
containers an item can be placed in.  We express these constraints in
interfaces.

Either a container or an object can provide constraints on the
containment relationship.

A container expresses constraints through a precondition on it's
`__setitem__` method in it's interface.

Preconditions can be simple callable objects, like functions. They
should raise a ``zope.interface.Invalid`` exception to indicate that a
constraint isn't satisfied:

   >>> import zope.interface

   >>> def preNoZ(container, name, ob):
   ...     "Silly precondition example"
   ...     if name.startswith("Z"):
   ...         raise zope.interface.Invalid("Names can not start with Z")

   >>> class I1(zope.interface.Interface):
   ...     def __setitem__(name, on):
   ...         "Add an item"
   ...     __setitem__.precondition = preNoZ

   >>> from dolmen.container.interfaces import IContainer
   >>> class C1(object):
   ...     zope.interface.implements(I1, IContainer)
   ...     def __repr__(self):
   ...         return 'C1'

Given such a precondition, we can then check whether an object can be
added:

   >>> c1 = C1()
   >>> checkObject(c1, "bob", None)
   >>> checkObject(c1, "Zbob", None)
   Traceback (most recent call last):
   ...
   Invalid: Names can not start with Z

We can also express constaints on the containers an object can be
added to. We do this by setting a field constraint on an object's
`__parent__` attribute:

   >>> import zope.schema

A field constraint is a callable object that returns a boolean value:

   >>> def con1(container):
   ...     "silly container constraint"
   ...     if not hasattr(container, 'x'):
   ...         return False
   ...     return True

   >>> class I2(zope.interface.Interface):
   ...     __parent__ = zope.schema.Field(constraint = con1)

   >>> class O(object):
   ...     zope.interface.implements(I2)

If the constraint isn't satisfied, we'll get a validation error when we
check whether the object can be added:

   >>> checkObject(c1, "bob", O())
   Traceback (most recent call last):
   ...
   ConstraintNotSatisfied: C1

Note that the validation error isn't very informative. For that
reason, it's better for constraints to raise Invalid errors when they
aren't satisfied:

   >>> def con1(container):
   ...     "silly container constraint"
   ...     if not hasattr(container, 'x'):
   ...         raise zope.interface.Invalid("What, no x?")
   ...     return True

   >>> class I2(zope.interface.Interface):
   ...     __parent__ = zope.schema.Field(constraint = con1)

   >>> class O(object):
   ...     zope.interface.implements(I2)

   >>> checkObject(c1, "bob", O())
   Traceback (most recent call last):
   ...
   Invalid: What, no x?

   >>> c1.x = 1
   >>> checkObject(c1, "bob", O())

The `checkObject` function is handy when checking whether we can add an
existing object to a container, but, sometimes, we want to check
whether an object produced by a factory can be added.  To do this, we
use `checkFactory`:

   >>> class Factory(object):
   ...     def __call__(self):
   ...         return O()
   ...     def getInterfaces(self):
   ...         return zope.interface.implementedBy(O)

   >>> factory = Factory()

   >>> checkFactory(c1, "bob", factory)
   True

   >>> del c1.x
   >>> checkFactory(c1, "bob", factory)
   False

Unlike `checkObject`, `checkFactory`:
  - Returns a boolean value
  - Takes a factory (e.g. a class) rather than an argument.

The container constraint we defined for C1 isn't actually used to
check the factory:

   >>> c1.x = 1
   >>> checkFactory(c1, "Zbob", factory)
   True

To work with `checkFactory`, a container precondition has to
implement a factory method.  This is because a factory, rather than
an object is passed.  To illustrate this, we'll make preNoZ its own
factory method:

   >>> preNoZ.factory = preNoZ

We can do this (silly thing) because preNoZ doesn't use the object
argument.

   >>> checkFactory(c1, "Zbob", factory)
   False
"""
__docformat__ = 'restructuredtext'

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
