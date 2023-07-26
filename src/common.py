import yaml


def read_config_file(config_file):
    """YAML format configuration 파일을 읽고 dictionary 형태로 return하는 함수

    Args:
        config_file (str): YAML format configuration 파일.

    Returns:
        dict: configuarion 정보 dictionary.
    """
    with open(config_file) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)

    return configs
