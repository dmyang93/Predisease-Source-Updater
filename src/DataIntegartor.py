from GenomicEntityPrediseasePair import GenomicEntityPrediseasePair


class DataIntegrator:
    def __init__(self):
        pass

    def convert_gencc_data(
        self,
        uuid2gencc_data: dict,
        mondo_id2omim_id: dict,
        mondo_id2orpha_id: dict,
    ) -> list:
        gp_pairs = list()
        for uuid in uuid2gencc_data:
            (
                hgnc_id,
                hgnc_symbol,
                phenotype_id,
                phenotype_title,
                _,
                _,
                _,
                confidence,
                _,
                moi,
                _,
                submitter,
                date,
                url,
                notes,
                pmids,
                criterial_url,
                run_date,
            ) = uuid2gencc_data[uuid]

            if mondo_id2omim_id.get(phenotype_id):
                new_phenotype_id = mondo_id2omim_id[phenotype_id]
            elif mondo_id2orpha_id.get(phenotype_id):
                new_phenotype_id = mondo_id2orpha_id[phenotype_id]
            else:
                new_phenotype_id = phenotype_id

            if not new_phenotype_id.startswith("OMIM"):
                gp_pair = GenomicEntityPrediseasePair(
                    hgnc_id,
                    hgnc_symbol,
                    new_phenotype_id,
                    phenotype_title,
                    confidence,
                    moi,
                    submitter,
                    date,
                    url,
                    notes,
                    pmids,
                    criterial_url,
                    run_date,
                )
                gp_pairs.append(gp_pair)

        return gp_pairs

    def convert_panelapp_data(self, panelapp_id2panelapp_data: dict):
        gp_pairs = list()
        for panelapp_id in panelapp_id2panelapp_data:
            (
                _,
                hgnc_id,
                hgnc_symbol,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                date,
                disorders,
                _,
                raw_phenotypes,
                confidence,
                moi,
                _,
                _,
                _,
                pmids,
            ) = panelapp_id2panelapp_data[panelapp_id]

            phenotype_id, phenotype_title = self.curate_panelapp_phenotype(
                raw_phenotypes
            )
            if not phenotype_id.startswith("OMIM"):
                gp_pair = GenomicEntityPrediseasePair(
                    hgnc_id,
                    hgnc_symbol,
                    phenotype_id,
                    phenotype_title,
                    confidence,
                    moi,
                    "PanelApp",
                    date,
                    _,
                    _,
                    pmids,
                    _,
                    _,
                )
            gp_pairs.append(gp_pair)

        return gp_pairs

    def curate_panelapp_phenotype(self, raw_phenotypes: list):
        phenotype_id, phenotype_title = "", ""
        return phenotype_id, phenotype_title
