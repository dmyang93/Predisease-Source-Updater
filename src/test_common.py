import pytest
from unittest import mock

from common import *


@mock.patch("builtins.open", new_callable=mock.mock_open)
def test_read_config_file(
    mock_opener,
):
    pass
