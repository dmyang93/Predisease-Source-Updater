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
