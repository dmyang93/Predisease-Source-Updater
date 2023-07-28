import pytest
from unittest import mock

from PanelappHandler import PanelappHandler


@pytest.fixture
@mock.patch("PanelappHandler.get_logger")
@mock.patch(
    "PanelappHandler.read_config_file",
    return_value=(
        {
            "PanelApp": {
                "API_URL": "https://panelapp.api.co.uk",
                "Key": {
                    "genes": [
                        "gene_key1",
                        {"gene_key2": ["subkey1", "subkey2"]},
                    ],
                    "strs": ["str_key1", "str_key2", "str_key3"],
                    "regions": ["region_key1", "region_key2"],
                },
            }
        }
    ),
)
def mock_panelapphandler(mock_config, mock_logger):
    panelapp_handler = PanelappHandler("log.txt", "config.yaml")

    return panelapp_handler


@mock.patch("requests.get")
def test_call_api(mock_requests_get, mock_panelapphandler):
    mock_requests_get.return_value.status_code = 200
    expected = "https://panelapp.api.co.uk/genes"
    mock_panelapphandler.call_api("genes")
    mock_requests_get.assert_called_with(expected)


@mock.patch("requests.get")
def test_call_paginated_api(mock_requests_get, mock_panelapphandler):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.side_effect = [
        {
            "count": 2,
            "next": "https://panelapp.genomicsengland.co.uk/api/v1/genes/2",
            "results": [{"a": 1, "b": [1, 2, 3], "c": None}],
        },
        {
            "count": 2,
            "next": None,
            "results": [{"a": 4, "b": [5, 6, 7], "c": "qwer"}],
        },
    ]
    expected = [
        {"a": 1, "b": [1, 2, 3], "c": None},
        {"a": 4, "b": [5, 6, 7], "c": "qwer"},
    ]

    assert expected == mock_panelapphandler.call_paginated_api("genes")


def test_extract_data_by_key(mock_panelapphandler):
    entity_panel_data = [
        {
            "entity_name": "ABCDEF",
            "panel": {"id": 1000},
            "gene_key1": "gene_val1",
            "gene_key2": {"subkey1": 1, "subkey2": 30},
            "gene_key3": "gene_val3",
        }
    ]
    entity = "genes"
    expected = {"ABCDEF_panel1000": ["gene_val1", 1, 30]}

    assert expected == mock_panelapphandler.extract_data_by_key(
        entity_panel_data, entity
    )
