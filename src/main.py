import os
import argparse

from common_utils import get_logger
from GenccHandler import GenccHandler
from PanelappHandler import PanelappHandler


def main(log_file_path: str, config_file_path: str, output_dir: str):
    """External source로부터 data를 받고, 정리하고, 통합하는 함수

    Args:
        log_file_path (str): log 파일 경로.
        config_file_path (str): configuration 파일 경로.
        output_dir (str): 다운로드된 파일 저장 디렉토리 경로.

    Note:
        External source:
            1) GenCC
            2) PanelApp
    """
    os.makedirs(output_dir, exist_ok=True)
    logger = get_logger(log_file_path)
    logger.info("0. Predisease-Source-Updater starts.")
    logger.info(f"   Output directory: {output_dir}")

    # GenCC
    gencc_handler = GenccHandler(logger, config_file_path, output_dir)
    logger.info("1. GenCC data update starts.")

    logger.info("1.1. GenCC raw data file download starts.")
    gencc_handler.download_raw_file()
    logger.info(f"     GenCC raw data file path: {gencc_handler.raw_file_path}")

    logger.info("1.2. GenCC raw data file is read.")
    uuid2gencc_data = gencc_handler.read_raw_file()
    logger.info(f"     Total count of GenCC data: {len(uuid2gencc_data)}")

    # PanelApp
    panelapp_handler = PanelappHandler(logger, config_file_path, output_dir)
    logger.info("2. PanelApp data update starts.")

    entities = ["genes", "strs", "regions"]
    panelapp_data = list()
    for idx, entity in enumerate(entities, start=1):
        logger.info(f"2.{idx}. PanelApp {entity} data.")

        logger.info(
            f"2.{idx}.1. PanelApp {entity} data by API response download starts."
        )
        panelapp_entity_data = panelapp_handler.call_paginated_api(entity)
        logger.info(f"       PanelApp {entity} data is downloaded.")

        logger.info(f"2.{idx}.2. PanelApp {entity} data is read.")
        panelapp_id2entity_data = panelapp_handler.extract_data_by_key(
            panelapp_entity_data, entity
        )
        logger.info(
            f"       Total count of PanelApp {entity} data: {len(panelapp_id2entity_data)}"
        )
        panelapp_data.append(panelapp_id2entity_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file_path", "-l")
    parser.add_argument("--config_file_path", "-c")
    parser.add_argument("--output_dir", "-o")
    args = parser.parse_args()

    main(args.log_file_path, args.config_file_path, args.output_dir)
