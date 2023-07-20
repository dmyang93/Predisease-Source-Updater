import yaml

def read_config_file(config_file):
    with open(config_file) as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
        
    return config_dict