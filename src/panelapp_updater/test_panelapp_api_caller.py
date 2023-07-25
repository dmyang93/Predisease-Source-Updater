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
        "major",
        "career",
    ]
    expected = {
        "HGNC:1111_panel1000": ["Tony", 3, 2, 1, "BI", ["seegene", "3billion"]]
    }

    assert expected == extract_data_by_key(gene_panel_datas, panelapp_keys)
