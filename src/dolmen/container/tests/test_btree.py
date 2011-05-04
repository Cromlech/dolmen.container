# -*- coding: utf-8 -*
"""BTree Container Tests
"""
from pytest import raises
from zope.interface.verify import verifyObject
from dolmen.container.components import BTreeContainer
from dolmen.container.interfaces import IBTreeContainer


def checkIterable(iterable):
    it = iter(iterable)
    assert callable(it.next)
    assert callable(it.__iter__)
    assert iter(it) is it

    # Exhaust the iterator:
    first_time = list(it)
    with raises(StopIteration):
        it.next()

    # Subsequent iterations will return the same values:
    assert list(iterable) == first_time
    assert list(iterable) == first_time


def test_stored_length():
    # This is lazy for backward compatibility.  If the len is not
    # stored already we set it to the length of the underlying
    # btree.
    bc = BTreeContainer()

    assert bc.__dict__['_BTreeContainer__len']() == 0
    del bc.__dict__['_BTreeContainer__len']
    assert not '_BTreeContainer__len' in bc.__dict__

    bc['1'] = 1
    assert len(bc) == 1
    assert bc.__dict__['_BTreeContainer__len']() == 1


def test_BTree_container_interface():
    bc = BTreeContainer()
    assert verifyObject(IBTreeContainer, bc)

    checkIterable(bc.items())
    checkIterable(bc.keys())
    checkIterable(bc.values())


def test_empty_items_with_arg():
    bc = BTreeContainer()

    assert list(bc.items(None)) == list(bc.items())
    assert list(bc.items("")) == []
    assert list(bc.items("not-there")) == []

    checkIterable(bc.items(None))
    checkIterable(bc.items(""))
    checkIterable(bc.items("not-there"))


def test_empty_keys_with_arg():
    bc = BTreeContainer()

    assert list(bc.keys(None)) == list(bc.keys())
    assert list(bc.keys("")) == []
    assert list(bc.keys("not-there")) == []

    checkIterable(bc.keys(None))
    checkIterable(bc.keys(""))
    checkIterable(bc.keys("not-there"))


def test_empty_values_with_arg():
    bc = BTreeContainer()

    assert list(bc.values(None)) == list(bc.values())
    assert list(bc.values("")) == []
    assert list(bc.values("not-there")) == []

    checkIterable(bc.values(None))
    checkIterable(bc.values(""))
    checkIterable(bc.values("not-there"))


def test_non_empty_items_with_arg():
    bc = BTreeContainer()
    bc["0"] = 1
    bc["1"] = 2
    bc["2"] = 3

    assert list(bc.items(None)) == list(bc.items())
    assert list(bc.items("")) == [("0", 1), ("1", 2), ("2", 3)]
    assert list(bc.items("3")) == []
    assert list(bc.items("2.")) == []
    assert list(bc.items("2")) == [("2", 3)]
    assert list(bc.items("1.")) == [("2", 3)]
    assert list(bc.items("1")) == [("1", 2), ("2", 3)]
    assert list(bc.items("0.")) == [("1", 2), ("2", 3)]
    assert list(bc.items("0")) == [("0", 1), ("1", 2), ("2", 3)]

    checkIterable(bc.items(None))
    checkIterable(bc.items(""))
    checkIterable(bc.items("0."))
    checkIterable(bc.items("3"))


def test_non_empty_keys_with_arg():
    bc = BTreeContainer()
    bc["0"] = 1
    bc["1"] = 2
    bc["2"] = 3

    assert list(bc.keys(None)) == list(bc.keys())
    assert list(bc.keys("")) == ["0", "1", "2"]
    assert list(bc.keys("3")) == []
    assert list(bc.keys("2.")) == []
    assert list(bc.keys("2")) == ["2"]
    assert list(bc.keys("1.")) == ["2"]
    assert list(bc.keys("1")) == ["1", "2"]
    assert list(bc.keys("0.")) == ["1", "2"]
    assert list(bc.keys("0")) == ["0", "1", "2"]

    checkIterable(bc.keys(None))
    checkIterable(bc.keys(""))
    checkIterable(bc.keys("0."))
    checkIterable(bc.keys("3"))


def test_non_empty_value_with_arg():
    bc = BTreeContainer()
    bc["0"] = 1
    bc["1"] = 2
    bc["2"] = 3

    assert list(bc.values(None)) == list(bc.values())
    assert list(bc.values("")) == [1, 2, 3]
    assert list(bc.values("3")) == []
    assert list(bc.values("2.")) == []
    assert list(bc.values("2")) == [3]
    assert list(bc.values("1.")) == [3]
    assert list(bc.values("1")) == [2, 3]
    assert list(bc.values("0.")) == [2, 3]
    assert list(bc.values("0")) == [1, 2, 3]

    checkIterable(bc.values(None))
    checkIterable(bc.values(""))
    checkIterable(bc.values("0."))
    checkIterable(bc.values("3"))


def test_correct_length_when_adding_existing_item():
    bc = BTreeContainer()

    bc[u'x'] = object()
    assert len(bc) == 1

    bc[u'x'] = bc[u'x']
    assert len(bc) == 1
    assert list(bc) == [u'x']
