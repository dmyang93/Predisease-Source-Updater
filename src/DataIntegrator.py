import re

from GenomicEntityPrediseasePair import GenomicEntityPrediseasePair


class DataIntegrator:
    def __init__(self):
        pass

    def convert_gencc_data(self, uuid2gencc_data: dict) -> list:
        gp_pairs = list()
        for uuid in uuid2gencc_data:
            (
                hgnc_id,
                hgnc_symbol,
                mondo_id,
                predisease_title,
                predisease_other_id,
                _,
                _,
                confidence,
                _,
                moi,
                _,
                submitter,
                evaluation_date,
                _,
                _,
                pmids_str,
                _,
                submission_date,
            ) = uuid2gencc_data[uuid]

            pmids = pmids_str.split(", ")

            gp_pair = GenomicEntityPrediseasePair(
                hgnc_id,
                hgnc_symbol,
                list(),
                "",
                mondo_id,
                [predisease_other_id],
                predisease_title,
                "",
                confidence,
                moi,
                pmids,
                submitter,
                evaluation_date,
                submission_date,
            )
            gp_pairs.append(gp_pair)

        return gp_pairs

    def convert_panelapp_data(self, panelapp_id2panelapp_data: dict) -> list:
        gp_pairs = list()
        for panelapp_id in panelapp_id2panelapp_data:
            (
                gene_name,
                hgnc_id,
                hgnc_symbol,
                omim_gene,
                gene_alias,
                gene_alias_name,
                _,
                panel_name,
                panel_disease_group,
                panel_disease_sub_group,
                _,
                relevant_disorders,
                submission_date,
                phenotypes,
                confidence,
                moi,
                mop,
                _,
                _,
                publications,
            ) = panelapp_id2panelapp_data[panelapp_id]

            gene_alias = self.concatenate_elements_to_one_string(
                gene_name, gene_alias, gene_alias_name
            )
            pmids = self.parse_ids(publications, 8)
            predisease_omim_ids = self.parse_ids(phenotypes, 6)
            predisease_alias = self.concatenate_elements_to_one_string(
                relevant_disorders
            )

            gp_pair = GenomicEntityPrediseasePair(
                hgnc_id,
                hgnc_symbol,
                omim_gene,
                gene_alias,
                "",
                predisease_omim_ids,
                panel_name,
                predisease_alias,
                confidence,
                moi,
                pmids,
                "PanelApp",
                "",
                "",
            )
            gp_pairs.append(gp_pair)

        return gp_pairs

    def concatenate_elements_to_one_string(*elements) -> str:
        one_string = ""
        for element in elements:
            if isinstance(element, str):
                one_string += element
            elif isinstance(element, list):
                one_string += ";".join(element)
            else:
                raise
            one_string += ";"

        return one_string

    def parse_ids(self, strings: list, digit_num: int) -> list:
        re = f"[0-9]{digit_num}"
        ids = list()
        for string in strings:
            id_search = re.search(string)
            if id_search:
                id_re = id_search.group(0)
                ids.append(id_re)

        return ids

    def extract_omim_ids(self, strings: str) -> list:
        omim_ids = list()
        omim_re1 = "^[0-9]{6}[^0-9]"
        omim_re2 = "[^0-9][0-9]{6}[^0-9]"
