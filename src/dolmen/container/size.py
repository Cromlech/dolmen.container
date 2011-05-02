# -*- coding: utf-8 -*-

from dolmen.container import ZopeMessageFactory as _
from zope.size.interfaces import ISized
from zope.interface import implements


class ContainerSized(object):
    implements(ISized)

    def __init__(self, container):
        self._container = container

    def sizeForSorting(self):
        """See `ISized`.
        """
        return ('item', len(self._container))

    def sizeForDisplay(self):
        """See `ISized`.
        """
        num_items = len(self._container)
        if num_items == 1:
            return _('1 item')
        return _('${items} items', mapping={'items': str(num_items)})
