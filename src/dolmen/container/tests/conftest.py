# -*- coding: utf-8 -*-

import pytest
from collections import deque
from zope.event import subscribers


events_queue = deque()


def stacker(event):
    events_queue.append(event)


@pytest.fixture(autouse=True)
def subscribe():
    subscribers.append(stacker)
    yield stacker
    subscribers.remove(stacker)
    events_queue.clear()


@pytest.fixture
def events():
    return events_queue
