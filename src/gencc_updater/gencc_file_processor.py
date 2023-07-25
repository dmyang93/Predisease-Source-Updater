import os
import sys
import unicodedata

GENCC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(GENCC_DIR)
sys.path.append(ROOT_DIR)
import common


def trim_line(splitted_line):
    """Trim words in list

    Args:
        splitted_line (list): list of splitted words.

    Returns:
        list: list of trimmed splitted words.
    """
    new_splitted_line = list()
    for splitted in splitted_line:
        new_splitted_line.append(
            splitted.strip(" ")
            .replace("\t", "")
            .replace('"', "")
            .replace("\xa0", "")
        )

    return new_splitted_line


def download_gencc_file(
    gencc_download_url: str, gencc_download_dir: str, gencc_raw_filename: str
) -> str:
    """wget을 이용해 GenCC data raw file을 정해진 디렉토리에 다운로드받고,
    그 파일의 절대 경로를 리턴하는 함수

    Args:
        gencc_download_url (str): GenCC 파일 다운로드를 위한 URL.
        gencc_download_dir (str): GenCC 파일 다운로드 위치.
        gencc_raw_filename (str): GenCC raw 파일 이름.

    Returns:
        str: GenCC raw 파일 경로.
    """
    gencc_raw_file = os.path.join(gencc_download_dir, gencc_raw_filename)
    download_command = f"wget -O {gencc_raw_file} {gencc_download_url}"
    os.system(download_command)

    return gencc_raw_file


def read_gencc_file(gencc_raw_file: str, gencc_keys: list) -> dict:
    """GenCC tsv 파일을 읽어서 trim한 뒤,
    GenCC UUID를 key로 하고, target하는 값들의 list를 value로 가진 dictionary로 리턴하는 함수
    target하는 값들의 key는 configuration을 통해 컨트롤된다.

    Args:
        gencc_raw_file (str): GenCC data tsv 파일.
        gencc_keys (list): 리턴할 dictionary에서 value에 들어갈 data에 대한 column들의 list.

    Returns:
        dict: GenCC UUID를 key로 하고, target하는 값들의 list를 value로 가진 dictionary.
    """
    key_indexes = list()
    uuid2gencc_data = dict()
    with open(gencc_raw_file) as f:
        for line in f:
            if line.startswith('"uuid"'):
                splitted_line = line.strip().split('"\t"')
                new_splitted_line = trim_line(splitted_line)
                for gencc_key in gencc_keys:
                    key_indexes.append(new_splitted_line.index(gencc_key))
                new_splitted_line = list()
            else:
                if line.startswith('"GENCC'):
                    if new_splitted_line:
                        uuid = new_splitted_line[0]
                        data = [new_splitted_line[i] for i in key_indexes]
                        uuid2gencc_data[uuid] = data
                    splitted_line = line.strip().split('"\t"')
                    new_splitted_line = trim_line(splitted_line)
                else:
                    splitted_line = line.strip().split('"\t"')
                    tmp_splitted_line = trim_line(splitted_line)
                    if new_splitted_line[-1].endswith(";"):
                        new_splitted_line[-1] += f"{tmp_splitted_line[0]}"
                    else:
                        new_splitted_line[-1] += f";{tmp_splitted_line[0]}"
                    if len(splitted_line) == 1:
                        pass
                    else:
                        new_splitted_line.extend(tmp_splitted_line[1:])
        uuid = new_splitted_line[0]
        data = [new_splitted_line[i] for i in key_indexes]
        uuid2gencc_data[uuid] = data

    return uuid2gencc_data


def main(config_file: str) -> dict:
    """Configuration 파일을 활용해 GenCC 데이터 파일을 다운로드 받아서,
    gene-phenotype 간 correlation raw 데이터에 대한 dictionary를 리턴하는 main 함수

    Args:
        config_file (str): configuration 파일 경로.

    Returns:
        dict: _description_
    """
    config = common.read_config_file(config_file)

    gencc_download_url = config["GenCC"]["download_url"]
    gencc_download_dir = config["GenCC"]["download_dir"]
    gencc_raw_filename = config["GenCC"]["raw_filename"]

    gencc_keys = config["Key"]

    gencc_raw_file = download_gencc_file(
        gencc_download_url, gencc_download_dir, gencc_raw_filename
    )
    uuid2gencc_data = read_gencc_file(gencc_raw_file, gencc_keys)

    return uuid2gencc_data
