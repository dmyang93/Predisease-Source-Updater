import os
import sys
import requests
import argparse

PANELAPP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PANELAPP_DIR)
sys.path.append(ROOT_DIR)
from common import read_config_file


def call_api(api_url: str) -> dict:
    """API call

    Args:
        api_url (str): API URL.

    Returns:
        (dict): API response로 받은 json 포맷 dictionary.
    """
    response = requests.get(api_url)
    api_call_data = response.json()

    return api_call_data


def call_paginated_api(api_url: str) -> list:
    """페이지 별로 나누어져 있는 연쇄적인 형태의 API를 call하고,
    response 내용 중 result 값들을 list로 출력하는 함수

    Args:
        api_url (str): API URL.

    Returns:
        (list): API response dictionary에서 'result' key의 value들만 모아놓은 list.
    """
    gene_panel_data = list()
    api_call_data = call_api(api_url)
    gene_panel_data.extend(api_call_data["results"])

    while api_call_data["next"] is not None:
        next_api_url = api_call_data["next"]
        api_call_data = call_api(next_api_url)
        gene_panel_data.extend(api_call_data["results"])

    return gene_panel_data


def extract_data_by_key(submitted_data: list, panelapp_keys: list) -> dict:
    """PanelApp API response로 받은 json dictionary 에서 추출한 데이터 list에서, \
        gene ID와 panel ID의 조합을 key로 하고, target하는 값들의 list를 value로 가진 \
            dictionary로 리턴하는 함수

    Args:
        submitted_data (list): PanelApp json dictionary에서 추출한 데이터 list.
        panelapp_keys (list): 리턴할 dictionary에서 value에 들어갈 data에 대한 key들의 list.

    Returns:
        (dict): gene ID와 panel ID의 조합을 key로 하고, \
            target하는 값들의 list를 value로 가진 dictionary.
            
    Note:
        target하는 값들의 key는 configuration을 통해 컨트롤된다.
        
    Examples:
        >>> submitted_data
        {
            "entity_name": "ABCDEF",
            "gene_data": {"hgnc_id": "HGNC:1111"},
            "panel": {"id": 1000},
            "name": "Tony",
            "age": 29,
            "major": "BI",
            "hobby": {"waterski": 1, "weight_training": 2, "game": 3},
            "apple": {
                "iphone": "first",
                "airpod": "second",
                "applewatch": "third",
            },
            "career": ["seegene", "3billion"]
        }
        >>> panelapp_keys
        [
            "name",
            {"hobby": ["game", "weight_training", "waterski"]},
            {"gene_data": ["hgnc_id"]},
            "major",
            "career"
        ]
        >>> entity_panel_id2panelapp_data
        {
            "ABCDEF_panel1000": ["Tony", 3, 2, 1, "HGNC:1111", "BI", ["seegene", "3billion"]]
        }

    """
    entity_panel_id2panelapp_data = dict()
    for submitted_datum in submitted_data:
        entity_id = submitted_datum["entity_name"]
        panel_id = submitted_datum["panel"]["id"]
        entity_panel_id = f"{entity_id}_panel{panel_id}"
        panelapp_vals = list()
        for panelapp_key in panelapp_keys:
            if isinstance(panelapp_key, str):
                panelapp_vals.append(submitted_datum[panelapp_key])
            elif isinstance(panelapp_key, dict):
                subkey = list(panelapp_key.keys())[0]
                for subval in list(panelapp_key.values())[0]:
                    panelapp_vals.append(submitted_datum[subkey][subval])
        entity_panel_id2panelapp_data[entity_panel_id] = panelapp_vals

    return entity_panel_id2panelapp_data


def main(config_file_path: str) -> dict:
    """PanelApp API URL을 configuration 파일에서 받아서,
    genomic entity-panel 간 correlation raw 데이터에 대한 dictionary들을
    리턴하는 main 함수

    Args:
        config_file (str): configuration 파일 경로.

    Returns:
        tuple: gene-panel / STR-panel / region-panel 간 correlation
        데이터에 대한 dictionary들
    """
    config = read_config_file(config_file_path)

    api_base_url = config["PanelApp"]["API_URL"]

    api_url = os.path.join(api_base_url, "genes")
    panelapp_gene_data = call_paginated_api(api_url)
    panelapp_gene_keys = config["Gene_Key"]
    panelapp_id2gene_data = extract_data_by_key(
        panelapp_gene_data, panelapp_gene_keys
    )

    api_url = os.path.join(api_base_url, "strs")
    panelapp_str_data = call_paginated_api(api_url)
    panelapp_str_keys = config["STR_Key"]
    panelapp_id2str_data = extract_data_by_key(
        panelapp_str_data, panelapp_str_keys
    )

    api_url = os.path.join(api_base_url, "regions")
    panelapp_region_data = call_paginated_api(api_url)
    panelapp_region_keys = config["Region_Key"]
    panelapp_id2region_data = extract_data_by_key(
        panelapp_region_data, panelapp_region_keys
    )

    return panelapp_id2gene_data, panelapp_id2str_data, panelapp_id2region_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get JSON by calling PanelAPP API and return dictionary for the data"
    )
    parser.add_argument(
        "--config_file_path", "-c", help="Configuration file path"
    )
    args = parser.parse.args()

    main(args.config_file_path)
