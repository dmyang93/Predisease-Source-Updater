import os
import pytest
from unittest import mock

from MondoImporter import MondoImporter


@pytest.fixture
@mock.patch(
    "MondoImporter.read_config_file",
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
def mock_mondoimporter(mock_config):
    mondo_importer = MondoImporter("log.txt", "config.yaml", "path/to/download")

    return mondo_importer


@mock.patch("os.path.exists")
@mock.patch("time.sleep")
@mock.patch("os.system", return_value=0)
def test_download_files(
    mock_os_system, mock_time_sleep, mock_os_path_exists, mock_mondoimporter
):
    download_url = mock_mondoimporter.config["download_url"]
    expected_cmd_calls = list()
    for file in mock_mondoimporter.files:
        expected_file = os.path.join(mock_mondoimporter.output_dir, file)
        expected_url = os.path.join(download_url, file)
        expected_cmd = f"wget -O {expected_file} {expected_url}"
        expected_cmd_calls.append(mock.call(expected_cmd))

    mock_mondoimporter.download_files()
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
def test_read_file(mock_opener, mock_mondoimporter):
    expected = {
        "MONDO:0001": "OMIM:0001",
        "MONDO:0002": "OMIM:0002",
        "MONDO:0003": "OMIM:0003",
        "MONDO:0004": "OMIM:0004",
    }
    mock_mondoimporter.mondo_id2omim_id = {"MONDO:0004": "OMIM:0004"}
    mock_mondoimporter.read_file("mock.tsv")
    assert expected == mock_mondoimporter.mondo_id2omim_id
