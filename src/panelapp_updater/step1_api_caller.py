import os
import requests
import common as common
from collections import defaultdict


def make_api_url(api_base_url, *path):
    """Maek full URL for API call.

    Args:
        api_base_url (str): API base URL.

    Returns:
        str: full API URL
    """
    api_url = os.path.join(api_base_url, *path)

    return api_url


def api_call(api_url):
    """_summary_

    Args:
        api_url (_type_): _description_

    Returns:
        _type_: _description_
    """
    response = requests.get(api_url)
    res_dict = response.json()

    return res_dict


def paginated_api_call(api_url):
    res_list = list()
    res_dict = api_call(api_url)
    res_list.extend(res_dict["results"])

    while res_dict["next"] is not None:
        next_api_url = res_dict["next"]
        res_dict = api_call(next_api_url)
        res_list.extend(res_dict["results"])

    return res_list


def get_value_by_key_from_list(dict_list, key):
    val_list = list()
    for dct in dict_list:
        val_list.append(dct[key])

    return val_list


def get_data_id_list(api_base_url, data_type, data_id_key):
    api_url = make_api_url(api_base_url, data_type)
    data_list = paginated_api_call(api_url)

    data_id_list = list()
    for data in data_list:
        data_id = data[data_id_key]
        data_id_list.append(data_id)

    data_id_list = list(set(data_id_list))

    return data_id_list


def get_panel_data(api_base_url, panel_id_list, panel_key_list):
    panel_data_dict = defaultdict(dict)
    for panel_id in panel_id_list:
        api_url = make_api_url(api_base_url, "panels", str(panel_id))
        panel_dict = api_call(api_url)
        for panel_key in panel_key_list:
            if isinstance(panel_key, str):
                if isinstance(panel_dict[panel_key], list):
                    panel_data_dict[panel_id][panel_key] = "::".join(
                        panel_dict[panel_key]
                    )
                else:
                    panel_data_dict[panel_id][panel_key] = panel_dict[panel_key]
            else:
                k, v = list(panel_key.items())[0]
                if isinstance(panel_dict[k], dict):
                    for subkey in v:
                        panel_data_dict[panel_id][subkey] = panel_dict[k][
                            subkey
                        ]
                else:
                    val_list = get_value_by_key_from_list(panel_dict[k], v)
                    panel_data_dict[panel_id][f"{k}_{v}"] = "::".join(val_list)

    return panel_data_dict


def get_gene_data(api_base_url, gene_id_list, gene_key_list):
    gene_data_dict = defaultdict(dict)
    for gene_id in gene_id_list:
        api_url = make_api_url(api_base_url, "genes", gene_id)
        gene_dict = api_call(api_url)
        gene_data_list = gene_dict["results"]

        for gene_data in gene_data_list:
            panel_id = gene_data["panel"]["id"]
            gene_data_dict[gene_id][panel_id] = dict()
            for gene_key in gene_key_list:
                if isinstance(gene_key, str):
                    if isinstance(gene_data[gene_key], list):
                        gene_data_dict[gene_id][panel_id][gene_key] = "::".join(
                            gene_data[gene_key]
                        )
                    else:
                        gene_data_dict[gene_id][panel_id][gene_key] = gene_data[
                            gene_key
                        ]
                else:
                    k, v = list(gene_key.items())[0]
                    if isinstance(v, str):
                        gene_data_dict[gene_id][panel_id][
                            f"{k}_{v}"
                        ] = gene_data[k][v]
                    else:
                        for subkey in v:
                            if isinstance(gene_data[k][subkey], str):
                                gene_data_dict[gene_id][panel_id][
                                    subkey
                                ] = gene_data[k][subkey]
                            elif isinstance(gene_data[k][subkey], list):
                                gene_data_dict[gene_id][panel_id][
                                    subkey
                                ] = "::".join(gene_data[k][subkey])
                            elif gene_data[k][subkey] is None:
                                gene_data_dict[gene_id][panel_id][subkey] = ""
                            else:
                                ensembl_id_list = list()
                                try:
                                    ensembl_id_37 = list(
                                        gene_data[k][subkey]["GRch37"].values()
                                    )[0]["ensembl_id"]
                                    ensembl_id_list.append(
                                        f"GRch37_{ensembl_id_37}"
                                    )
                                except KeyError:
                                    pass
                                try:
                                    ensembl_id_38 = list(
                                        gene_data[k][subkey]["GRch38"].values()
                                    )[0]["ensembl_id"]
                                    ensembl_id_list.append(
                                        f"GRch38_{ensembl_id_38}"
                                    )
                                except KeyError:
                                    pass
                                gene_data_dict[gene_id][panel_id][
                                    subkey
                                ] = "::".join(ensembl_id_list)

    return gene_data_dict


def api_caller(config_file):
    config_dict = common.read_config_file(config_file)

    api_base_url = config_dict["panelApp"]["API_URL"]
    panel_key_list = config_dict["panel_key"]
    gene_key_list = config_dict["gene_key"]

    panel_id_list = get_data_id_list(api_base_url, "panels", "id")
    gene_id_list = get_data_id_list(api_base_url, "genes", "entity_name")
    str_id_list = get_data_id_list(api_base_url, "strs", "entity_name")
    region_id_list = get_data_id_list(api_base_url, "regions", "entity_name")

    panel_data_dict = get_panel_data(
        api_base_url, panel_id_list, panel_key_list
    )
    gene_data_dict = get_gene_data(api_base_url, gene_id_list, gene_key_list)
