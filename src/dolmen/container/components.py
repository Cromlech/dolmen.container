# -*- coding: utf-8 -*-

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from dolmen.container.interfaces import IContainer, IBTreeContainer
from dolmen.container.contained import Contained, setitem, uncontained
from zope.interface import implements


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
