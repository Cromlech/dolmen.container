dolmen.container
****************

This package defines interfaces of container components, and provides
container implementations. Three components are available, one generic
non-persistent (ZODB-wise) one, `Container` and two ZODB-aware BTree
containers : `BTreeContainer` and `OrderedBTreeContainer`.

The package also provides some utilities to handle containers :
an implementation of a `zope.size.ISized` component and an
implementation of a `zope.location.ISublocations` component. They can
both be registered as adapters, but `dolmen.container` doesn't do it
by default.

This package is the fruit of a fork from `zope.container`, in order to
free it from the heavy zope dependencies and from the C
module. Therefore, the behavior is different : the ContainedProxy
component does not allow a transparent persistency.
