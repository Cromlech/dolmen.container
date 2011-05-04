# -*- coding: utf-8 -*-

import pytest
from zope.interface.verify import verifyObject
from dolmen.container.components import Container
from dolmen.container.interfaces import IContainer


DATA = [('3', '0'), ('2', '1'), ('4', '2'), ('6', '3'), ('0', '4'),
        ('5', '5'), ('1', '6'), ('8', '7'), ('7', '8'), ('9', '9')]


def make_container():
    container = Container()
    for k, v in DATA:
        container[k] = v
    return container


def testIContainerVerify():
    verifyObject(IContainer, make_container())


def test_keys():
    # See interface IReadContainer
    container = Container()
    keys = container.keys()
    assert list(keys) == []

    container = make_container()
    keys = container.keys()
    keys = list(keys)
    keys.sort()  # convert to sorted list
    ikeys = [k for k, v in DATA]
    ikeys.sort()  # sort input keys
    assert keys == ikeys


def test_get():
    # See interface IReadContainer
    default = object()
    container = Container()

    with pytest.raises(KeyError):
        container.__getitem__(DATA[0][0])

    assert container.get(DATA[0][0], default) is default

    container = make_container()
    with pytest.raises(KeyError):
        container.__getitem__("cromlech")

    assert container.get("cromlech", default) is default

    for i in (1, 8, 7, 3, 4):
        assert container.get(DATA[i][0], default) == DATA[i][1]
        assert container.get(DATA[i][0]) == DATA[i][1]


def test_values():
    # See interface IReadContainer
    container = Container()
    values = container.values()
    assert list(values) == []

    container = make_container()
    values = list(container.values())

    for k, v in DATA:
        try:
            values.remove(v)
        except ValueError:
            raise KeyError('Value not in list')

    assert values == []


def test_len():
    # See interface IReadContainer
    container = Container()
    assert not len(container)

    container = make_container()
    assert len(container) == len(DATA)


def test_items():
    # See interface IReadContainer
    container = Container()
    items = container.items()
    assert list(items) == []

    container = make_container()
    items = container.items()
    items = list(items)
    items.sort()  # convert to sorted list
    data = [(k, v) for k, v in DATA]
    data.sort()
    assert items == data


def test___contains__():
    # See interface IReadContainer
    container = Container()
    assert not DATA[6][0] in container

    container = make_container()
    assert DATA[6][0] in container
    for i in (1, 8, 7, 3, 4):
        assert DATA[i][0] in container


def test_delObject():
    # See interface IWriteContainer
    default = object()
    container = Container()

    with pytest.raises(KeyError):
        container.__delitem__(DATA[0][0])

    container = make_container()
    with pytest.raises(KeyError):
        container.__delitem__("cromlech")

    for i in (1, 8, 7, 3, 4):
        del container[DATA[i][0]]

    for i in (1, 8, 7, 3, 4):
        with pytest.raises(KeyError):
            container.__getitem__(DATA[i][0])
        assert container.get(DATA[i][0], default) is default

    for i in (0, 2, 9, 6, 5):
        assert container[DATA[i][0]] == DATA[i][1]
