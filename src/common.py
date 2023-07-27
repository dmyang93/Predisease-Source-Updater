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
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
