import os
import time
import json
import requests
from logging import Logger

from common_utils import read_config_file


class PanelappDownloader:
    def __init__(self, logger: Logger, config_file_path: str, output_dir: str):
        config = read_config_file(config_file_path)
        self.logger = logger
        self.config = config["PanelApp"]
        self.output_dir = output_dir

    def call_api(self, additional_url_path: str) -> dict:
        """API call

        Args:
            additional_url_path (str): API call을 위한 추가적인 URL.

        Returns:
            (dict): API response로 받은 json 포맷 dictionary.

        Note:
            API call은 10초 간격으로 3번까지 시도한 후, 1시간 뒤에 마지막으로 1번 더 시도한다.
        """
        api_url = os.path.join(self.config["API_URL"], additional_url_path)

        trial, max_trial = 1, 3
        while trial <= max_trial:
            response = requests.get(api_url)
            if response.status_code == 200:
                break
            time.sleep(10)
            trial += 1

        if response.status_code != 200:
            time.sleep(3600)
            response = requests.get(api_url)
            if response.status_code != 200:
                self.logger.error("PanelApp data is not downloaded.")
                self.logger.error(f"Failed API URL: {api_url}")
                raise Exception(
                    f"APIError: {response.status_code} {response.reason}"
                )

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
            
        Note:
            result 값을 모두 합쳐 json 파일에 write를 한다.
        """
        entity_panel_data = list()
        panelapp_api_data = self.call_api(entity)
        entity_panel_data.extend(panelapp_api_data["results"])

        while panelapp_api_data["next"] is not None:
            next_api_url = panelapp_api_data["next"]
            additional_api_url = os.path.join(
                entity, os.path.basename(next_api_url)
            )
            panelapp_api_data = self.call_api(additional_api_url)
            entity_panel_data.extend(panelapp_api_data["results"])

        entity_panel_data4json = dict()
        entity_panel_data4json["results"] = entity_panel_data
        entity_panel_data_json_path = os.path.join(
            self.output_dir, f"panelapp_{entity}.json"
        )
        with open(
            entity_panel_data_json_path, "w", encoding="utf-8"
        ) as json_write:
            json.dump(
                entity_panel_data4json, json_write, ensure_ascii=False, indent=4
            )

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
                "ABCDEF_panel1000": ["Tony", 3, 2, 1, "HGNC:1111", 
                                     "BI", ["seegene", "3billion"]]
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
