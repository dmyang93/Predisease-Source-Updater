import os
import requests

from common import read_config_file, get_logger


class PanelappHandler:
    def __init__(self, log_file_path: str, config_file_path: str):
        config = read_config_file(config_file_path)
        self.logger = get_logger(log_file_path)
        self.config = config["PanelApp"]

    def call_api(self, additional_url_path):
        """API call

        Args:
            additional_url_path (str): API call을 위한 추가적인 URL.

        Returns:
            (dict): API response로 받은 json 포맷 dictionary.
        """
        api_url = self.config["API_URL"]
        api_url = os.path.join(api_url, additional_url_path)
        response = requests.get(api_url)
        panelapp_api_data = response.json()

        return panelapp_api_data

    def call_paginated_api(self, entity: str) -> list:
        """페이지 별로 나누어져 있는 연쇄적인 형태의 API를 call하고, \
        response 내용 중 result 값들을 list로 출력하는 함수

        Args:
            entity (str): API URL 구성을 위한 entity 종류.
                choice) "genes", "strs", "regions"

        Returns:
            (list): API response dictionary에서 'result' key의 value들만 모아놓은 list.
        """
        entity_panel_data = list()
        panelapp_api_data = self.call_api(entity)
        entity_panel_data.extend(panelapp_api_data["results"])

        while panelapp_api_data["next"] is not None:
            next_api_url = panelapp_api_data["next"]
            panelapp_api_data = self.call_api(next_api_url)
            entity_panel_data.extend(panelapp_api_data["results"])

        return entity_panel_data

    def extract_data_by_key(self, entity_panel_data: list, entity: str) -> dict:
        """PanelApp API response로 받은 json dictionary 에서 추출한 데이터 list에서, \
        entity ID와 panel ID의 조합을 key로 하고, target하는 값들의 list를 value로 가진 \
            dictionary로 리턴하는 함수

        Args:
            entity_panel_data (list): PanelApp json dictionary에서 추출한 데이터 list.
            entity (str): entity 종류. choice) "genes", "strs", "regions"

        Returns:
            (dict): gene ID와 panel ID의 조합을 key로 하고, \
                target하는 값들의 list를 value로 가진 dictionary.
                
        Note:
            target하는 값들의 key는 configuration을 통해 컨트롤된다.
            
        Examples:
            >>> entity_panel_data
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
            >>> self.config["Key"][entity]
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

        for submitted_datum in entity_panel_data:
            entity_id = submitted_datum["entity_name"]
            panel_id = submitted_datum["panel"]["id"]
            entity_panel_id = f"{entity_id}_panel{panel_id}"
            panelapp_vals = list()

            for panelapp_key in self.config["Key"][entity]:
                if isinstance(panelapp_key, str):
                    panelapp_vals.append(submitted_datum[panelapp_key])
                elif isinstance(panelapp_key, dict):
                    subkey = list(panelapp_key.keys())[0]
                    for subval in list(panelapp_key.values())[0]:
                        panelapp_vals.append(submitted_datum[subkey][subval])

            entity_panel_id2panelapp_data[entity_panel_id] = panelapp_vals

        return entity_panel_id2panelapp_data
