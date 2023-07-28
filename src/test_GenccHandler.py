import pytest
from unittest import mock

from GenccHandler import GenccHandler


@pytest.fixture
@mock.patch("GenccHandler.get_logger")
@mock.patch(
    "GenccHandler.read_config_file",
    return_value={
        "GenCC": {
            "download_url": "https://blah-blah.com",
            "Key": ["col1", "col3"],
        }
    },
)
def mock_gencchandler(mock_config, mock_logger):
    gencc_handler = GenccHandler("log.txt", "config.yaml", "path/to/download")

    return gencc_handler


@pytest.mark.parametrize(
    "split_lines,expected",
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
def test_trim_line(mock_gencchandler, split_lines, expected):
    assert expected == mock_gencchandler.trim_line(split_lines)


@mock.patch("os.path.exists")
@mock.patch("time.sleep")
@mock.patch("os.system", return_value=0)
def test_download_raw_file(
    mock_os_system, mock_time_sleep, mock_os_path_exsits, mock_gencchandler
):
    expected_url = mock_gencchandler.config["download_url"]
    expected = f"wget -O {mock_gencchandler.raw_file_path} {expected_url}"

    mock_gencchandler.download_raw_file()
    mock_os_system.assert_called_with(expected)


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=(
        '"uuid"\t"col1"\t"col2"\t"col3"\n'
        '"GENCCid1"\t"col1val1"\t"col2val1"\t"col3val1"\n'
        '"GENCCid2"\t"col1val2"\t"col2val2"\t"col3\tval2"\n'
        '"GENCCid3"\t"col1val3"\t"col2val3"\t"col3\nval3"\n'
        '"GENCCid4"\t"col1val4"\t"col2val4"\t"col3\n\nval4"'
    ),
)
def test_read_raw_file(mock_open, mock_gencchandler):
    expected = {
        "GENCCid1": ["col1val1", "col3val1"],
        "GENCCid2": ["col1val2", "col3val2"],
        "GENCCid3": ["col1val3", "col3;val3"],
        "GENCCid4": ["col1val4", "col3;val4"],
    }
    assert expected == mock_gencchandler.read_raw_file()
