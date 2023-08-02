import yaml
import logging


def read_config_file(config_file_path: str) -> dict:
    """YAML format configuration 파일을 읽고 dictionary 형태로 return하는 함수

    Args:
        config_file (str): YAML format configuration 파일.

    Returns:
        (dict): configuarion 정보 dictionary.
    """
    with open(config_file_path) as config_open:
        config = yaml.load(config_open, Loader=yaml.FullLoader)

    return config


def get_logger(log_file_path: str):
    """logger를 만들고 포맷팅해주는 함수

    Args:
        log_file_path (str): log 파일 경로

    Returns:
        (Logger): logger object
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s"
    )
    file_handler = logging.FileHandler(
        log_file_path,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def read_mondo_file(mondo_file_path: str) -> dict:
    headers = [
        "class_label",
        "synonyms",
        "GARD",
        "NCIT",
        "OMIM",
        "DOID",
        "Orphanet",
    ]

    mondo_id2data = dict()
    with open(mondo_file_path) as mondo_open:
        for line in mondo_open:
            if line.startswith("class"):
                header_lines = line.strip().split("\t")
                indexes = [header_lines.index(header) for header in headers]
            else:
                data_lines = line.strip().split("\t")
                mondo_id = data_lines[0]
                mondo_id2data[mondo_id] = dict()
                for idx in indexes:
                    mondo_id2data[mondo_id][header_lines[idx]] = data_lines[idx]

    return mondo_id2data
