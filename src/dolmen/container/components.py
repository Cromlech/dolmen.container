# -*- coding: utf-8 -*-

from persistent import Persistent
from persistent.list import PersistentList
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from zope.interface import implements

from dolmen.container.contained import Contained, setitem, uncontained
from dolmen.container.contained import notifyContainerModified
from dolmen.container.interfaces import (
    IContainer, IBTreeContainer, IOrderedContainer)


class Lazy(object):
    """Lazy Attributes.
    """

    def __init__(self, func, name=None):
        if name is None:
            name = func.__name__
        self.data = (func, name)

    def __get__(self, inst, class_):
        if inst is None:
            return self

        func, name = self.data
        value = func(inst)
        inst.__dict__[name] = value

        return value


class Container(Contained):
    """Non-persistent container.
    """
    implements(IContainer)

    def __init__(self):
        self._data = self._create_container()

    def _create_container(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has `get`,
        `has_key`, `keys`, `items`, and `values` methods.
        """
        return {}

    def keys(self):
        """See interface `IReadContainer`.
        """
        return self._data.keys()

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        """See interface `IReadContainer`.
        """
        return self._data[key]

    def get(self, key, default=None):
        """See interface `IReadContainer`.
        """
        return self._data.get(key, default)

    def values(self):
        """See interface `IReadContainer`.
        """
        return self._data.values()

    def __len__(self):
        """See interface `IReadContainer`.
        """
        return len(self._data)

    def items(self):
        """See interface `IReadContainer`.
        """
        return self._data.items()

    def __contains__(self, key):
        """See interface `IReadContainer`.
        """
        return key in self._data

    has_key = __contains__

    def __setitem__(self, key, object):
        """See interface `IWriteContainer`.
        """
        setitem(self, self._data.__setitem__, key, object)

    def __delitem__(self, key):
        """See interface `IWriteContainer`.
        """
        uncontained(self._data[key], self, key)
        del self._data[key]


class BTreeContainer(Container, Persistent):
    """Persistent container, using ZODB BTree.
    """
    implements(IBTreeContainer)

    def __init__(self):
        Container.__init__(self)
        self.__len = Length()

    def _create_container(self):
        """OOBTree by default.
        """
        return OOBTree()

    @Lazy
    def _BTreeContainer__len(self):
        l = Length()
        ol = len(self._data)
        if ol > 0:
            l.change(ol)
        self._p_changed = True
        return l

    def __len__(self):
        return self.__len()

    def _setitemf(self, key, value):
        # make sure our lazy property gets set
        l = self.__len
        self._data[key] = value
        l.change(1)

    def __setitem__(self, key, value):
        setitem(self, self._setitemf, key, value)

    def __delitem__(self, key):
        # make sure our lazy property gets set
        l = self.__len
        uncontained(self._data[key], self, key)
        del self._data[key]
        l.change(-1)

    def items(self, key=None):
        return self._data.items(key)

    def keys(self, key=None):
        return self._data.keys(key)

    def values(self, key=None):
        return self._data.values(key)


class OrderedBTreeContainer(BTreeContainer):

    implements(IOrderedContainer)

    def __init__(self):
        super(OrderedBTreeContainer, self).__init__()
        self._order = PersistentList()

    def keys(self):
        return self._order[:]

    def values(self):
        return (self[key] for key in self._order)

    def items(self):
        return ((key, self[key]) for key in self._order)

    def __setitem__(self, key, object):
        exists = key in self
        if not exists:
            self._order.append(key)
        try:
            super(OrderedBTreeContainer, self).__setitem__(key, object)
        except Exception, e:
            if not exists:
                self._order.remove(key)
            raise e
        return key

    def __delitem__(self, key):
        super(OrderedBTreeContainer, self).__delitem__(key)
        self._order.remove(key)

    def updateOrder(self, order):
        """Impose a new order on the items in this container.

        Items in this container are, by default, returned in the order
        in which they were inserted.  To change the order, provide an
        argument to this method that is a sequence containing every key
        already in the container, but in a new order.
        """
        if set(order) != set(self._order):
            raise ValueError("Incompatible key set.")

        self._order = PersistentList()
        self._order.extend(order)
        notifyContainerModified(self)
