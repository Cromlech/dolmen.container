# -*- coding: utf-8 -*-

import zope.component

from zope.broken.interfaces import IBroken
from zope.interface import implements
from zope.event import notify
from zope.location.interfaces import IContained, ILocation, ISublocations
from zope.lifecycleevent import (
    ObjectModifiedEvent, ObjectMovedEvent,
    ObjectAddedEvent, ObjectRemovedEvent)

from zope.location import LocationProxy
from dolmen.container import ZopeMessageFactory as _
from dolmen.container.interfaces import (
    INameChooser, IReservedNames, NameReserved, IContainerModifiedEvent)


class Contained(object):
    """Stupid mix-in that defines `__parent__` and `__name__` attributes.
    """
    implements(IContained)

    __parent__ = __name__ = None


class ContainedProxy(LocationProxy):
    implements(IContained)


class ContainerModifiedEvent(ObjectModifiedEvent):
    """The container has been modified.
    """
    implements(IContainerModifiedEvent)


def dispatchToSublocations(object, event):
    """Dispatch an event to sublocations of a given object

    When a move event happens for an object, it's important to notify
    subobjects as well.
    """
    subs = ISublocations(object, None)
    if subs is not None:
        for sub in subs.sublocations():
            for ignored in zope.component.subscribers((sub, event), None):
                pass  # They do work in the adapter fetch


class ContainerSublocations(object):
    """Basic implementation of an `ISublocations`
    """
    implements(ISublocations)

    def __init__(self, container):
        self.container = container

    def sublocations(self):
        container = self.container
        for key in container:
            yield container[key]


def containedEvent(object, container, name=None):
    """Establish the containment of the object in the container.
    """
    if not IContained.providedBy(object):
        if ILocation.providedBy(object):
            zope.interface.alsoProvides(object, IContained)
        else:
            object = ContainedProxy(object)

    oldparent = object.__parent__
    oldname = object.__name__

    if oldparent is container and oldname == name:
        # No events
        return object, None

    object.__parent__ = container
    object.__name__ = name

    if oldparent is None or oldname is None:
        event = ObjectAddedEvent(object, container, name)
    else:
        event = ObjectMovedEvent(object, oldparent, oldname, container, name)

    return object, event


def contained(object, container, name=None):
    """Establishes the containment of the object in the container
    """
    return containedEvent(object, container, name)[0]


def notifyContainerModified(object, *descriptions):
    """Notifies that the container was modified.
    """
    notify(ContainerModifiedEvent(object, *descriptions))


def setitem(container, setitemf, name, object):
    """Helper function to set an item and generate needed events

    This helper is needed, in part, because the events need to get
    published after the `object` has been added to the `container`.
    """
    # Do basic name check:
    if isinstance(name, str):
        try:
            name = unicode(name)
        except UnicodeError:
            raise TypeError("name not unicode or ascii string")
    elif not isinstance(name, unicode):
        raise TypeError("name not unicode or ascii string")

    if not name:
        raise ValueError("empty names are not allowed")

    old = container.get(name)
    if old is object:
        return
    if old is not None:
        raise KeyError(name)

    object, event = containedEvent(object, container, name)
    setitemf(name, object)
    if event:
        notify(event)
        notifyContainerModified(container)


fixing_up = False


def uncontained(object, container, name=None):
    try:
        oldparent = object.__parent__
        oldname = object.__name__
    except AttributeError:
        # The old object doesn't implements IContained
        # Maybe we're converting old data:
        if not fixing_up:
            raise
        oldparent = None
        oldname = None

    if oldparent is not container or oldname != name:
        if oldparent is not None or oldname is not None:
            notifyContainerModified(container)
        return

    event = ObjectRemovedEvent(object, oldparent, oldname)
    notify(event)

    if not IBroken.providedBy(object):
        object.__parent__ = None
        object.__name__ = None
    notifyContainerModified(container)


class NameChooser(object):

    implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):

        if isinstance(name, str):
            name = unicode(name)
        elif not isinstance(name, unicode):
            raise TypeError("Invalid name type", type(name))

        if not name:
            raise ValueError(
                _("An empty name was provided. Names cannot be empty."))

        if name[:1] in '+@' or '/' in name:
            raise ValueError(
                _("Names cannot begin with '+' or '@' or contain '/'"))

        reserved = IReservedNames(self.context, None)
        if reserved is not None:
            if name in reserved.reservedNames:
                raise NameReserved(name)

        if name in self.context:
            raise KeyError(
                _("The given name is already being used"))

        return True

    def chooseName(self, name, object):

        container = self.context

        # convert to unicode and remove checkName unallowed characters
        try:
            name = unicode(name)
        except:
            name = u''
        name = name.replace('/', '-').lstrip('+@')

        if not name:
            name = unicode(object.__class__.__name__)

        # for an existing name, append a number.
        # We should keep client's os.path.extsep (not ours), we assume it's '.'
        dot = name.rfind('.')
        if dot >= 0:
            suffix = name[dot:]
            name = name[:dot]
        else:
            suffix = ''

        n = name + suffix
        i = 1
        while n in container:
            i += 1
            n = name + u'-' + unicode(i) + suffix

        # Make sure the name is valid.  We may have started with something bad.
        self.checkName(n, object)

        return n
