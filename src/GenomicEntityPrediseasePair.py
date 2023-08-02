class GenomicEntityPrediseasePair:
    def __init__(
        self,
        hgnc_id: str,
        hgnc_symbol: str,
        phenotype_id: str,
        phenotype_title: str,
        phenotype_alias: list,
        confidence: str,
        moi: str,
        submitter: str,
    ):
        self.hgnc_id = hgnc_id
        self.hgnc_symbol = hgnc_symbol
        self.phenotype_id = phenotype_id
        self.phenotype_title = phenotype_title
        self.phenotype_alias = phenotype_alias
        self.confidence = confidence
        self.moi = moi
        self.submitter = submitter
