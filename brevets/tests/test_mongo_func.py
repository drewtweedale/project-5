"""
Nose tests for acp_times.py

Write your tests HERE AND ONLY HERE.
"""
import arrow
from acp_times import open_time, close_time
from mongo_file import get_brev, insert_brev
import nose    # Testing framework
import logging

from unittest.mock import MagicMock

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)


def test_get_brev():
    test_data = []
    collection = MagicMock()
    # Test when the collection is empty.
    assert (get_brev(collection) == [])

def test_insert_brev():
    test_data = []
    collection = MagicMock()
    # Test when the collection is empty.
    assert (insert_brev(collection) == [])