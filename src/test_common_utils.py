from unittest import mock

from common_utils import read_config_file


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=(
        "PanelApp:\n"
        "  API_URL: https://panelapp.api.co.uk\n\n"
        ""
        "Gene_key:\n"
        "  - gene_data:\n"
        "    - gene_key1\n"
        "    - gene_key2\n"
        "  - gene_key3"
    ),
)
def test_read_config_file(mock_opener):
    config_file = "config.yaml"
    expected = {
        "PanelApp": {"API_URL": "https://panelapp.api.co.uk"},
        "Gene_key": [{"gene_data": ["gene_key1", "gene_key2"]}, "gene_key3"],
    }

    assert expected == read_config_file(config_file)
