import os
import pytest
from unittest import mock

from MondoImporter import MondoHandler


@pytest.fixture
@mock.patch(
    "MondoHandler.read_config_file",
    return_value={
        "MONDO": {
            "download_url": "https://mondo.download.com",
            "file_list": [
                "mondo_broadmatch_omim.tsv",
                "mondo_exactmatch_omim.tsv",
                "mondo_broadmatch_orpha.tsv",
                "mondo_exactmatch_orpha.tsv",
            ],
        }
    },
)
def mock_mondohandler(mock_config):
    mondo_handler = MondoHandler("log.txt", "config.yaml", "path/to/download")

    return mondo_handler


@mock.patch("os.path.exists")
@mock.patch("time.sleep")
@mock.patch("os.system", return_value=0)
def test_download_files(
    mock_os_system, mock_time_sleep, mock_os_path_exists, mock_mondohandler
):
    download_url = mock_mondohandler.config["download_url"]
    expected_cmd_calls = list()
    for file in mock_mondohandler.files:
        expected_file = os.path.join(mock_mondohandler.output_dir, file)
        expected_url = os.path.join(download_url, file)
        expected_cmd = f"wget -O {expected_file} {expected_url}"
        expected_cmd_calls.append(mock.call(expected_cmd))

    mock_mondohandler.download_files()
    mock_os_system.assert_has_calls(expected_cmd_calls)


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=(
        "#This is a MONDO-OMIM file data for mocking\n"
        "subject_id\tsubject_label\tpredicate_id\tobject_id\tobject_label\tmapping\n"
        "MONDO:0001\tdisease 0001\tskos:exactmatch\tOMIM:0001\tdisease 0001\tManual\n"
        "MONDO:0002\tdisease 0002\tskos:exactmatch\tOMIM:0002\tdisease 0002\tManual\n"
        "MONDO:0003\tdisease 0003\tskos:exactmatch\tOMIM:0003\tdisease 0003\tManual\n"
    ),
)
def test_read_file(mock_opener, mock_mondohandler):
    expected = {
        "MONDO:0001": "OMIM:0001",
        "MONDO:0002": "OMIM:0002",
        "MONDO:0003": "OMIM:0003",
        "MONDO:0004": "OMIM:0004",
    }
    mock_mondohandler.mondo_id2omim_id = {"MONDO:0004": "OMIM:0004"}
    mock_mondohandler.read_file("mock.tsv")
    assert expected == mock_mondohandler.mondo_id2omim_id
