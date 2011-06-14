# -*- coding: utf-8 -*-

from cromlech.container.interfaces import IContainer


class IBTreeContainer(IContainer):
    """Container that supports BTree semantics for some methods.
    """

    def items(key=None):
        """Return an iterator over the key-value pairs in the container.

        If ``None`` is passed as `key`, this method behaves as if no argument
        were passed; exactly as required for ``IContainer.items()``.

        If `key` is in the container, the first item provided by the iterator
        will correspond to that key.  Otherwise, the first item will be for
        the key that would come next if `key` were in the container.
        """

    def keys(key=None):
        """Return an iterator over the keys in the container.

        If ``None`` is passed as `key`, this method behaves as if no argument
        were passed; exactly as required for ``IContainer.keys()``.

        If `key` is in the container, the first key provided by the iterator
        will be that key.  Otherwise, the first key will be the one that would
        come next if `key` were in the container.
        """

    def values(key=None):
        """Return an iterator over the values in the container.

        If ``None`` is passed as `key`, this method behaves as if no argument
        were passed; exactly as required for ``IContainer.values()``.

        If `key` is in the container, the first value provided by the iterator
        will correspond to that key.  Otherwise, the first value will be for
        the key that would come next if `key` were in the container.
        """
