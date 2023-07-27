import os
import sys
import argparse
import logging

GENCC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(GENCC_DIR)
sys.path.append(ROOT_DIR)
from common import read_config_file


def trim_line(split_lines: list) -> list:
    """Trim words in list

    Args:
        split_lines (list): list of split words.

    Returns:
        (list): list of trimmed split words.

    Examples:
        >>> split_lines
        [
            "\"id1",
            "HGNC:00001",
            "PMID:\xa030827498",
            "MIM 618494\t",
            "autism spectrum disorder\""
        ]
        >>> new_split_lines
        [
            "id1",
            "HGNC:0001",
            "PMID:30827498",
            "MIM 618494",
            "autism spectrum disorder
        ]
    """
    new_split_lines = list()
    for split in split_lines:
        new_split_lines.append(
            split.strip(" ")
            .replace("\t", "")
            .replace('"', "")
            .replace("\xa0", "")
        )

    return new_split_lines


def download_gencc_file(
    gencc_download_url: str, gencc_download_dir: str, gencc_raw_filename: str
) -> str:
    """wget을 이용해 GenCC data raw file을 정해진 디렉토리에 다운로드받고, \
        그 파일의 절대 경로를 리턴하는 함수

    Args:
        gencc_download_url (str): GenCC 파일 다운로드를 위한 URL.
        gencc_download_dir (str): GenCC 파일 다운로드 위치.
        gencc_raw_filename (str): GenCC raw 파일 이름.

    Returns:
        (str): GenCC raw 파일 경로.
    """
    gencc_raw_file = os.path.join(gencc_download_dir, gencc_raw_filename)
    download_command = f"wget -O {gencc_raw_file} {gencc_download_url}"
    os.system(download_command)

    return gencc_raw_file


def read_gencc_file(gencc_raw_file: str, gencc_keys: list) -> dict:
    """GenCC tsv 파일을 읽어서 trim한 뒤, \
        GenCC UUID를 key로 하고, target하는 값들의 list를 value로 가진 dictionary로 리턴하는 함수

    Args:
        gencc_raw_file (str): GenCC data tsv 파일.
        gencc_keys (list): 리턴할 dictionary에서 value에 들어갈 data에 대한 column들의 list.

    Returns:
        (dict): GenCC UUID를 key로 하고, target하는 값들의 list를 value로 가진 dictionary.

    Note:
        target하는 값들의 key는 configuration을 통해 컨트롤된다.
        
    Examples:
        >>> file_open = open(gencc_raw_file)
        >>> data = file_open.readlines()
        >>> data
        [
            "\"uuid\"\t\"gene_name\"\t\"phenotype_name\"\t\"confidence\"\n", 
            "\"GENCC1\"\t\"gene_aa\"\t\"phenotype_8503\"\t\"strong\"\n",
            "\"GENCC2\"\t\"gene_kc\"\t\"phenotype_0239\"\t\"moderate\"\n", 
            "\"GENCC3\"\t\"gene_xs\"\t\"phenotype_1174\"\t\"weak\"\n"
        ]
        >>> gencc_keys
        ["phtenotye_name", "gene_name", "confidence"]
        >>> uuid2gencc_data
        {
            "GENCC1": ["phenotype_8503", "gene_aa", "strong"], 
            "GENCC2": ["phenotype_0239", "gene_kc", "moderate"], 
            "GENCC": ["phenotype_1174", "gene_xs", "weak]
        }
         
         """
    uuid2gencc_data = dict()
    with open(gencc_raw_file) as file_open:
        for line in file_open:
            if line.startswith('"uuid"'):
                split_lines = line.strip().split('"\t"')
                new_split_lines = trim_line(split_lines)
                key_indexes = [
                    new_split_lines.index(gencc_key) for gencc_key in gencc_keys
                ]
                new_split_lines = list()
            elif line.startswith('"GENCC'):
                if new_split_lines:
                    uuid = new_split_lines[0]
                    data = [new_split_lines[idx] for idx in key_indexes]
                    uuid2gencc_data[uuid] = data
                split_lines = line.strip().split('"\t"')
                new_split_lines = trim_line(split_lines)
            else:
                split_lines = line.strip().split('"\t"')
                tmp_split_lines = trim_line(split_lines)
                if new_split_lines[-1].endswith(";"):
                    new_split_lines[-1] += f"{tmp_split_lines[0]}"
                else:
                    new_split_lines[-1] += f";{tmp_split_lines[0]}"
                if len(split_lines) != 1:
                    new_split_lines.extend(tmp_split_lines[1:])
        uuid = new_split_lines[0]
        data = [new_split_lines[idx] for idx in key_indexes]
        uuid2gencc_data[uuid] = data

    return uuid2gencc_data


def main(config_file_path: str) -> dict:
    """Configuration 파일을 활용해 GenCC 데이터 파일을 다운로드 받아서, \
        gene-phenotype 간 correlation raw 데이터에 대한 dictionary를 리턴하는 main 함수

    Args:
        config_file_path (str): configuration 파일 경로.

    Returns:
        (dict): submit된 gene-phenotype pair를 key로 갖고, \
            submit된 추가 데이터를 value로 갖는 dictionary
    """
    config = read_config_file(config_file_path)

    gencc_download_url = config["GenCC"]["download_url"]
    gencc_download_dir = config["GenCC"]["download_dir"]
    gencc_raw_filename = config["GenCC"]["raw_filename"]

    gencc_keys = config["Key"]

    gencc_raw_file_path = download_gencc_file(
        gencc_download_url, gencc_download_dir, gencc_raw_filename
    )
    uuid2gencc_data = read_gencc_file(gencc_raw_file_path, gencc_keys)

    return uuid2gencc_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download GenCC file and return dictionary for the raw data from the file"
    )
    parser.add_argument("--config_file", "-c", help="Configuration file path")
    args = parser.parse.args()

    main(args.config_file_path)
