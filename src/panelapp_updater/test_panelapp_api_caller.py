import pytest
from unittest import mock

from panelapp_api_caller import *


@pytest.mark.parametrize(
    "api_base_url,path,expected",
    [
        (
            "https://panelapp.genomicsengland.co.uk/api/v1",
            "genes",
            "https://panelapp.genomicsengland.co.uk/api/v1/genes",
        ),
    ],
)
def test_make_api_url(api_base_url, path, expected):
    assert expected == make_api_url(api_base_url, path)


@mock.patch("requests.get")
def test_api_call(mock_requests_get):
    mock_requests_get.return_value.json.return_value = {
        "a": 1,
        "b": [1, 2, 3],
        "c": None,
    }
    api_url = "https://panelapp.genomicsengland.co.uk/api/v1/genes"
    expected = {"a": 1, "b": [1, 2, 3], "c": None}

    assert expected == api_call(api_url)


@mock.patch("requests.get")
def test_paginated_api_call(mock_requests_get):
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
    api_url = "https://panelapp.genomicsengland.co.uk/api/v1/genes/1"
    expected = [
        {"a": 1, "b": [1, 2, 3], "c": None},
        {"a": 4, "b": [5, 6, 7], "c": "qwer"},
    ]

    assert expected == paginated_api_call(api_url)


def test_extract_data_by_key():
    gene_panel_datas = [
        {
            "entity_name": "ABCDEF",
            "gene_data": {"hgnc_id": "HGNC:1111"},
            "panel": {"id": 1000},
            "name": "Tony",
            "age": 29,
            "major": "BI",
            "hobby": {"waterski": 1, "weight_training": 2, "game": 3},
            "apple": {
                "iphone": "first",
                "airpod": "second",
                "applewatch": "third",
            },
            "career": ["seegene", "3billion"],
        }
    ]
    panelapp_keys = [
        "name",
        {"hobby": ["game", "weight_training", "waterski"]},
        {"gene_data": ["hgnc_id"]},
        "major",
        "career",
    ]
    expected = {
        "ABCDEF_panel1000": [
            "Tony",
            3,
            2,
            1,
            "HGNC:1111",
            "BI",
            ["seegene", "3billion"],
        ]
    }

    assert expected == extract_data_by_key(gene_panel_datas, panelapp_keys)


@mock.patch(
    "panelapp_api_caller.extract_data_by_key",
    side_effect=[
        {"geneid_panelid": ["gene_val1", "gene_val2"]},
        {"strid_panelid": ["str_val1", "str_val2", "str_val3"]},
        {"regionid_panelid": ["region_val1", "region_val2"]},
    ],
)
@mock.patch(
    "panelapp_api_caller.paginated_api_call",
    side_effect=[
        {
            "id": "geneid",
            "panel_id": "panelid",
            "gene_key1": "gene_val1",
            "gene_key2": "gene_val2",
        },
        {
            "id": "strid",
            "panel_id": "panelid",
            "str_key1": "str_val1",
            "str_key2": "str_val2",
            "str_key3": "str_val3",
        },
        {
            "id": "regionid",
            "panel_id": "panelid",
            "region_key1": "region_val1",
            "region_key2": "region_val2",
        },
    ],
)
@mock.patch(
    "common.read_config_file",
    return_value={
        "PanelApp": {"API_URL": "https://panelapp.api.co.uk"},
        "Gene_Key": ["gene_key1", "gene_key2"],
        "STR_Key": ["str_key1", "str_key2", "str_key3"],
        "Region_Key": ["region_key1", "region_key2"],
    },
)
def test_main(mock_config, mock_apicall, mock_extract):
    config_file = "config.yaml"
    expected = (
        {"geneid_panelid": ["gene_val1", "gene_val2"]},
        {"strid_panelid": ["str_val1", "str_val2", "str_val3"]},
        {"regionid_panelid": ["region_val1", "region_val2"]},
    )

    assert expected == main(config_file)
    assert mock_apicall.call_count == 3
    assert mock_extract.call_count == 3
