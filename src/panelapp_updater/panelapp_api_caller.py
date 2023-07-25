import os
import sys
import requests

PANELAPP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PANELAPP_DIR)
sys.path.append(ROOT_DIR)
import common


def make_api_url(api_base_url: str, *path) -> str:
    """경로를 입력 받아, API call을 위한 전체 API URL을 만드는 함수

    Args:
        api_base_url (str): API base URL.

    Returns:
        str: 전체 API URL.
    """
    api_url = os.path.join(api_base_url, *path)

    return api_url


def api_call(api_url: str) -> dict:
    """API call

    Args:
        api_url (str): API URL.

    Returns:
        dict: API response로 받은 json 포맷 dictionary.
    """
    response = requests.get(api_url)
    api_call_data = response.json()

    return api_call_data


def paginated_api_call(api_url: str) -> list:
    """페이지 별로 나누어져 있는 연쇄적인 형태의 API를 call하고,
    response 내용 중 result 값들을 list로 출력하는 함수

    Args:
        api_url (str): API URL.

    Returns:
        list: API response dictionary에서 'result' key의 value들만 모아놓은 list.
    """
    gene_panel_datas = list()
    api_call_data = api_call(api_url)
    gene_panel_datas.extend(api_call_data["results"])

    while api_call_data["next"] is not None:
        next_api_url = api_call_data["next"]
        api_call_data = api_call(next_api_url)
        gene_panel_datas.extend(api_call_data["results"])

    return gene_panel_datas


def extract_data_by_key(gene_panel_datas: list, panelapp_keys: list) -> dict:
    """PanelApp API response로 받은 json dictionary 에서 추출한 데이터 list에서,
    gene ID와 panel ID의 조합을 key로 하고, target하는 값들의 list를 value로 가진 dictionary로 리턴하는 함수
    target하는 값들의 key는 configuration을 통해 컨트롤된다.

    Args:
        gene_panel_datas (list): PanelApp json dictionary에서 추출한 데이터 list.
        panelapp_keys (list): 리턴할 dictionary에서 value에 들어갈 data에 대한 key들의 list.

    Returns:
        dict: gene ID와 panel ID의 조합을 key로 하고,
        target하는 값들의 list를 value로 가진 dictionary.
    """
    entity_panel_id2panelapp_data = dict()
    for gene_panel_data in gene_panel_datas:
        entity_id = gene_panel_data["entity_name"]
        panel_id = gene_panel_data["panel"]["id"]
        entity_panel_id = f"{entity_id}_panel{panel_id}"
        panelapp_vals = list()
        for panelapp_key in panelapp_keys:
            if isinstance(panelapp_key, str):
                panelapp_vals.append(gene_panel_data[panelapp_key])
            elif isinstance(panelapp_key, dict):
                subkey = list(panelapp_key.keys())[0]
                for subval in list(panelapp_key.values())[0]:
                    panelapp_vals.append(gene_panel_data[subkey][subval])
        entity_panel_id2panelapp_data[entity_panel_id] = panelapp_vals

    return entity_panel_id2panelapp_data

    # for gene_id in gene_id_list:
    #     api_url = make_api_url(api_base_url, "genes", gene_id)
    #     gene_dict = api_call(api_url)
    #     gene_data_list = gene_dict["results"]

    #     for gene_data in gene_data_list:
    #         panel_id = gene_data["panel"]["id"]
    #         gene_data_dict[gene_id][panel_id] = dict()
    #         for gene_key in gene_key_list:
    #             if isinstance(gene_key, str):
    #                 if isinstance(gene_data[gene_key], list):
    #                     gene_data_dict[gene_id][panel_id][gene_key] = "::".join(
    #                         gene_data[gene_key]
    #                     )
    #                 else:
    #                     gene_data_dict[gene_id][panel_id][gene_key] = gene_data[
    #                         gene_key
    #                     ]
    #             else:
    #                 k, v = list(gene_key.items())[0]
    #                 if isinstance(v, str):
    #                     gene_data_dict[gene_id][panel_id][
    #                         f"{k}_{v}"
    #                     ] = gene_data[k][v]
    #                 else:
    #                     for subkey in v:
    #                         if isinstance(gene_data[k][subkey], str):
    #                             gene_data_dict[gene_id][panel_id][
    #                                 subkey
    #                             ] = gene_data[k][subkey]
    #                         elif isinstance(gene_data[k][subkey], list):
    #                             gene_data_dict[gene_id][panel_id][
    #                                 subkey
    #                             ] = "::".join(gene_data[k][subkey])
    #                         elif gene_data[k][subkey] is None:
    #                             gene_data_dict[gene_id][panel_id][subkey] = ""
    #                         else:
    #                             ensembl_id_list = list()
    #                             try:
    #                                 ensembl_id_37 = list(
    #                                     gene_data[k][subkey]["GRch37"].values()
    #                                 )[0]["ensembl_id"]
    #                                 ensembl_id_list.append(
    #                                     f"GRch37_{ensembl_id_37}"
    #                                 )
    #                             except KeyError:
    #                                 pass
    #                             try:
    #                                 ensembl_id_38 = list(
    #                                     gene_data[k][subkey]["GRch38"].values()
    #                                 )[0]["ensembl_id"]
    #                                 ensembl_id_list.append(
    #                                     f"GRch38_{ensembl_id_38}"
    #                                 )
    #                             except KeyError:
    #                                 pass
    #                             gene_data_dict[gene_id][panel_id][
    #                                 subkey
    #                             ] = "::".join(ensembl_id_list)


def main(config_file: str) -> dict:
    """PanelApp API URL을 configuration 파일에서 받아서,
    genomic entity-panel 간 correlation raw 데이터에 대한 dictionary를 리턴하는 main 함수

    Args:
        config_file (str): configuration 파일 경로.

    Returns:
        dict: _description_
    """
    configs = common.read_config_file(config_file)

    api_base_url = configs["PanelApp"]["API_URL"]

    api_url = make_api_url(api_base_url, "genes")
    panelapp_gene_datas = paginated_api_call(api_url)
    panelapp_gene_keys = configs["Gene_Key"]
    panelapp_id2gene_data = extract_data_by_key(
        panelapp_gene_datas, panelapp_gene_keys
    )

    api_url = make_api_url(api_base_url, "strs")
    panelapp_str_datas = paginated_api_call(api_url)
    panelapp_str_keys = configs["STR_Key"]
    panelapp_id2str_data = extract_data_by_key(
        panelapp_str_datas, panelapp_str_keys
    )

    api_url = make_api_url(api_base_url, "regions")
    panelapp_region_datas = paginated_api_call(api_url)
    panelapp_region_keys = configs["Region_Key"]
    panelapp_id2region_data = extract_data_by_key(
        panelapp_region_datas, panelapp_region_keys
    )

    return panelapp_id2gene_data, panelapp_id2str_data, panelapp_id2region_data
