import pytest
from unittest import mock

from gencc_file_processor import *


@pytest.mark.parametrize(
    "splitted_line,expected",
    [
        (["col1", "col2", "col3"], ["col1", "col2", "col3"]),
        ([" col1", "col2", " col3"], ["col1", "col2", "col3"]),
        (["col1", "col2", "col3.1\tcol3.2"], ["col1", "col2", "col3.1col3.2"]),
        (["col1", "col2", '"col3', 'col4"'], ["col1", "col2", "col3", "col4"]),
        (
            ["col1", "col2", "col3.1\xa0col3.2"],
            ["col1", "col2", "col3.1col3.2"],
        ),
    ],
)
def test_trim_line(splitted_line, expected):
    assert expected == trim_line(splitted_line)


@mock.patch("os.system")
def test_download_gencc_file(mock_os_system):
    gencc_download_url = (
        "https://search.thegencc.org/download/action/submissions-export-tsv"
    )
    gencc_download_dir = "/home/ubuntu/tony/data/gencc_downlaod"
    gencc_raw_filename = "submission-export-tsv"
    gencc_raw_file = (
        "/home/ubuntu/tony/data/gencc_downlaod/submission-export-tsv"
    )
    gencc_download_cmd = f"wget -O {gencc_raw_file} {gencc_download_url}"

    gencc_raw_file = download_gencc_file(
        gencc_download_url, gencc_download_dir, gencc_raw_filename
    )
    mock_os_system.assert_called_with(gencc_download_cmd)


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data="""\"uuid\"\t\"col1\"\t\"col2\"\t\"col3\"\n\"GENCCid1\"\t\"col1val1\"\t\"col2val1\"\t\"col3val1\"\n\"GENCCid2\"\t\"col1val2\"\t\"col2val2\"\t\"col3\tval2\"\n\"GENCCid3\"\t\"col1val3\"\t\"col2val3\"\t\"col3\nval3\"\n\"GENCCid4\"\t\"col1val4\"\t\"col2val4\"\t\"col3\n\nval4\"""",
)
def test_read_gencc_file(mock_open):
    gencc_raw_file = "submissions-export-tsv"
    gencc_keys = ["col1", "col3"]
    expected = {
        "GENCCid1": ["col1val1", "col3val1"],
        "GENCCid2": ["col1val2", "col3val2"],
        "GENCCid3": ["col1val3", "col3;val3"],
        "GENCCid4": ["col1val4", "col3;val4"],
    }

    assert expected == read_gencc_file(gencc_raw_file, gencc_keys)


@mock.patch(
    "gencc_file_processor.read_gencc_file",
    return_value={
        "ASDF": [1, 2, 3, ["a", "b", "c"], None, ["xd", "xf"]],
        "OMRX": [9, 2, 4, ["k", "s", "m"], "qq", ["xd", "xl"]],
    },
)
@mock.patch(
    "gencc_file_processor.download_gencc_file",
    return_value="/home/ubuntu/path/to/download/raw_filename.tsv",
)
@mock.patch(
    "common.read_config_file",
    return_value={
        "GenCC": {
            "download_url": "https://blah-blah.com",
            "download_dir": "/home/ubuntu/path/to/download",
            "raw_filename": "raw_filename.tsv",
        },
        "Key": ["a", "b", "c", {"d": [1, 2, 3]}],
    },
)
def test_main(mock_config, mock_download, mock_read):
    config_file = "config.yaml"
    expected = {
        "ASDF": [1, 2, 3, ["a", "b", "c"], None, ["xd", "xf"]],
        "OMRX": [9, 2, 4, ["k", "s", "m"], "qq", ["xd", "xl"]],
    }

    assert expected == main(config_file)
    mock_config.assert_called()
    mock_download.assert_called()
    mock_read.assert_called()
