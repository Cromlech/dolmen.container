# -*- coding: utf-8 -*-

import zope.component
import zope.interface.declarations

from zope.broken.interfaces import IBroken
from zope.interface import providedBy, implements
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecification
from zope.event import notify
from zope.location.interfaces import IContained, ILocation, ISublocations
from zope.security.checker import selectChecker, CombinedChecker
from zope.lifecycleevent import (
    ObjectModifiedEvent, ObjectMovedEvent,
    ObjectAddedEvent, ObjectRemovedEvent)

from zope.location import LocationProxy
from zope.proxy import getProxiedObject
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

       We do this based on locations.

       Suppose, for example, that we define some location objects.

         >>> class L(object):
         ...     implements(ILocation)
         ...     def __init__(self, name):
         ...         self.__name__ = name
         ...         self.__parent__ = None
         ...     def __repr__(self):
         ...         return '%s(%s)' % (
         ...                 self.__class__.__name__, str(self.__name__))

         >>> class C(L):
         ...     implements(ISublocations)
         ...     def __init__(self, name, *subs):
         ...         L.__init__(self, name)
         ...         self.subs = subs
         ...         for sub in subs:
         ...             sub.__parent__ = self
         ...     def sublocations(self):
         ...         return self.subs

         >>> c = C(1,
         ...       C(11,
         ...         L(111),
         ...         L(112),
         ...         ),
         ...       C(12,
         ...         L(121),
         ...         L(122),
         ...         L(123),
         ...         L(124),
         ...         ),
         ...       L(13),
         ...       )

       Now, if we call the dispatcher, it should call event handlers
       for all of the objects.

       Lets create an event handler that records the objects it sees:

         >>> seen = []
         >>> def handler(ob, event):
         ...     seen.append((ob, event.object))

       Note that we record the the object the handler is called on as
       well as the event object:

       Now we'll register it:

         >>> from zope import component
         >>> from zope.lifecycleevent.interfaces import IObjectMovedEvent
         >>> component.provideHandler(handler, [None, IObjectMovedEvent])

       We also register our dispatcher:

         >>> component.provideHandler(dispatchToSublocations,
         ...   [None, IObjectMovedEvent])

       We can then call the dispatcher for the root object:

         >>> event = ObjectRemovedEvent(c)
         >>> dispatchToSublocations(c, event)

       Now, we should have seen all of the subobjects:

         >>> seenreprs = map(repr, seen)
         >>> seenreprs.sort()
         >>> seenreprs
         ['(C(11), C(1))', '(C(12), C(1))', '(L(111), C(1))',""" \
          """ '(L(112), C(1))', '(L(121), C(1))', '(L(122), C(1))',""" \
          """ '(L(123), C(1))', '(L(124), C(1))', '(L(13), C(1))']

       We see that we get entries for each of the subobjects and
       that,for each entry, the event object is top object.

       This suggests that location event handlers need to be aware that
       the objects they are called on and the event objects could be
       different.

    """
    subs = ISublocations(object, None)
    if subs is not None:
        for sub in subs.sublocations():
            for ignored in zope.component.subscribers((sub, event), None):
                pass # They do work in the adapter fetch


class ContainerSublocations(object):
    """Get the sublocations for a container

       Obviously, this is the container values:

         >>> class MyContainer(object):
         ...     def __init__(self, **data):
         ...         self.data = data
         ...     def __iter__(self):
         ...         return iter(self.data)
         ...     def __getitem__(self, key):
         ...         return self.data[key]

         >>> container = MyContainer(x=1, y=2, z=42)
         >>> adapter = ContainerSublocations(container)
         >>> sublocations = list(adapter.sublocations())
         >>> sublocations.sort()
         >>> sublocations
         [1, 2, 42]

    """
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

    If the item implements `IContained`, simply set its `__parent__`
    and `__name__` attributes:

    >>> class IItem(zope.interface.Interface):
    ...     pass
    >>> class Item(Contained):
    ...     implements(IItem)
    ...     def setAdded(self, event):
    ...         self.added = event
    ...     def setMoved(self, event):
    ...         self.moved = event

    >>> from zope.lifecycleevent.interfaces import IObjectAddedEvent
    >>> from zope.lifecycleevent.interfaces import IObjectMovedEvent

    >>> from zope import component
    >>> component.provideHandler(lambda obj, event: obj.setAdded(event),
    ...   [IItem, IObjectAddedEvent])
    >>> component.provideHandler(lambda obj, event: obj.setMoved(event),
    ...   [IItem, IObjectMovedEvent])

    >>> item = Item()

    >>> container = {}
    >>> setitem(container, container.__setitem__, u'c', item)
    >>> container[u'c'] is item
    1
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'c'

    If we run this using the testing framework, we'll use `getEvents` to
    track the events generated:

    >>> from zope.component.eventtesting import getEvents
    >>> from zope.lifecycleevent.interfaces import IObjectModifiedEvent

    We have an added event:

    >>> len(getEvents(IObjectAddedEvent))
    1
    >>> event = getEvents(IObjectAddedEvent)[-1]
    >>> event.object is item
    1
    >>> event.newParent is container
    1
    >>> event.newName
    u'c'
    >>> event.oldParent
    >>> event.oldName

    As well as a modification event for the container:

    >>> len(getEvents(IObjectModifiedEvent))
    1
    >>> getEvents(IObjectModifiedEvent)[-1].object is container
    1

    The item's hooks have been called:

    >>> item.added is event
    1
    >>> item.moved is event
    1

    We can suppress events and hooks by setting the `__parent__` and
    `__name__` first:

    >>> item = Item()
    >>> item.__parent__, item.__name__ = container, 'c2'
    >>> setitem(container, container.__setitem__, u'c2', item)
    >>> len(container)
    2
    >>> len(getEvents(IObjectAddedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    1

    >>> getattr(item, 'added', None)
    >>> getattr(item, 'moved', None)

    If the item had a parent or name (as in a move or rename),
    we generate a move event, rather than an add event:

    >>> setitem(container, container.__setitem__, u'c3', item)
    >>> len(container)
    3
    >>> len(getEvents(IObjectAddedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    2
    >>> len(getEvents(IObjectMovedEvent))
    2

    (Note that we have 2 move events because add are move events.)

    We also get the move hook called, but not the add hook:

    >>> event = getEvents(IObjectMovedEvent)[-1]
    >>> getattr(item, 'added', None)
    >>> item.moved is event
    1

    If we try to replace an item without deleting it first, we'll get
    an error:

    >>> setitem(container, container.__setitem__, u'c', [])
    Traceback (most recent call last):
    ...
    KeyError: u'c'


    >>> del container[u'c']
    >>> setitem(container, container.__setitem__, u'c', [])
    >>> len(getEvents(IObjectAddedEvent))
    2
    >>> len(getEvents(IObjectModifiedEvent))
    3


    If the object implements `ILocation`, but not `IContained`, set it's
    `__parent__` and `__name__` attributes *and* declare that it
    implements `IContained`:

    >>> from zope.location import Location
    >>> item = Location()
    >>> IContained.providedBy(item)
    0
    >>> setitem(container, container.__setitem__, u'l', item)
    >>> container[u'l'] is item
    1
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'l'
    >>> IContained.providedBy(item)
    1

    We get new added and modification events:

    >>> len(getEvents(IObjectAddedEvent))
    3
    >>> len(getEvents(IObjectModifiedEvent))
    4

    If the object doesn't even implement `ILocation`, put a
    `ContainedProxy` around it:

    >>> item = []
    >>> setitem(container, container.__setitem__, u'i', item)
    >>> container[u'i']
    []
    >>> container[u'i'] is item
    0
    >>> item = container[u'i']
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'i'
    >>> IContained.providedBy(item)
    1

    >>> len(getEvents(IObjectAddedEvent))
    4
    >>> len(getEvents(IObjectModifiedEvent))
    5

    We'll get type errors if we give keys that aren't unicode or ascii keys:

    >>> setitem(container, container.__setitem__, 42, item)
    Traceback (most recent call last):
    ...
    TypeError: name not unicode or ascii string

    >>> setitem(container, container.__setitem__, None, item)
    Traceback (most recent call last):
    ...
    TypeError: name not unicode or ascii string

    >>> setitem(container, container.__setitem__, 'hello ' + chr(200), item)
    Traceback (most recent call last):
    ...
    TypeError: name not unicode or ascii string

    and we'll get a value error of we give an empty string or unicode:

    >>> setitem(container, container.__setitem__, '', item)
    Traceback (most recent call last):
    ...
    ValueError: empty names are not allowed

    >>> setitem(container, container.__setitem__, u'', item)
    Traceback (most recent call last):
    ...
    ValueError: empty names are not allowed

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

        # convert to unicode and remove characters that checkName does not allow
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
