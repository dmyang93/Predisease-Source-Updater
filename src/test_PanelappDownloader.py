import pytest
from unittest import mock

from PanelappDownloader import PanelappDownloader


@pytest.fixture
@mock.patch(
    "PanelappDownloader.read_config_file",
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
def mock_panelappdownloader(mock_config):
    panelapp_downloader = PanelappDownloader(
        "log.txt", "config.yaml", "path/to/output"
    )

    return panelapp_downloader


@mock.patch("requests.get")
def test_call_api(mock_requests_get, mock_panelappdownloader):
    mock_requests_get.return_value.status_code = 200
    expected = "https://panelapp.api.co.uk/genes"
    mock_panelappdownloader.call_api("genes")
    mock_requests_get.assert_called_with(expected)


@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("requests.get")
def test_call_paginated_api(
    mock_requests_get, mock_open, mock_panelappdownloader
):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.side_effect = [
        {
            "count": 3,
            "next": "https://panelapp.genomicsengland.co.uk/api/v1/genes/2",
            "results": [{"a": 1, "b": [1, 2, 3], "c": None}],
        },
        {
            "count": 3,
            "next": "https://panelapp.genomicsengland.co.uk/api/v1/genes/3",
            "results": [{"a": 4, "b": [5, 6, 7], "c": "qwer"}],
        },
        {
            "count": 3,
            "next": None,
            "results": [{"a": 2, "b": [0, 10, 20], "c": "jkl"}],
        },
    ]
    expected = [
        {"a": 1, "b": [1, 2, 3], "c": None},
        {"a": 4, "b": [5, 6, 7], "c": "qwer"},
        {"a": 2, "b": [0, 10, 20], "c": "jkl"},
    ]

    assert expected == mock_panelappdownloader.call_paginated_api("genes")


def test_extract_data_by_key(mock_panelappdownloader):
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

    assert expected == mock_panelappdownloader.extract_data_by_key(
        entity_panel_data, entity
    )
