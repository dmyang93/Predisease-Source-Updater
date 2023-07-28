import argparse

from GenccHandler import GenccHandler
from PanelappHandler import PanelappHandler


def main(log_file_path, config_file_path, output_dir):
    """External source로부터 data를 받고, 정리하고, 통합하는 함수

    Args:
        log_file_path (str): log 파일 경로.
        config_file_path (str): configuration 파일 경로.
        output_dir (str): 다운로드된 파일 저장 장소.

    Note:
        External source:
            1) GenCC
            2) PanelApp
    """
    # GenCC
    gencc_handler = GenccHandler(log_file_path, config_file_path, output_dir)
    panelapp_handler = PanelappHandler(log_file_path, config_file_path)

    gencc_handler.download_raw_file()

    # PanelApp
    panelapp_handler = PanelappHandler(log_file_path, config_file_path)
    uuid2gencc_data = gencc_handler.read_raw_file()

    entity = "genes"
    panelapp_gene_data = panelapp_handler.call_paginated_api(entity)
    panelapp_id2gene_data = panelapp_handler.extract_data_by_key(
        panelapp_gene_data, entity
    )
    entity = "strs"
    panelapp_str_data = panelapp_handler.call_paginated_api("strs")
    panelapp_id2str_data = panelapp_handler.extract_data_by_key(
        panelapp_str_data, entity
    )
    entity = "regions"
    panelapp_region_data = panelapp_handler.call_paginated_api(entity)
    panelapp_id2region_data = panelapp_handler.extract_data_by_key(
        panelapp_region_data, entity
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file_path", "-l")
    parser.add_argument("--config_file_path", "-c")
    parser.add_argument("--output_dir", "-o")
    args = parser.parse_args()

    main(args.log_file_path, args.config_file_path, args.output_dir)
