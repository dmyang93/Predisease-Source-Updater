class GenomicEntityPrediseasePair:
    def __init__(
        self,
        hgnc_id,
        hgnc_symbol,
        phenotype_id,
        phenotype_title,
        confidence,
        moi,
        submitter,
    ):
        self.hgnc_id = hgnc_id
        self.hgnc_symbol = hgnc_symbol
        self.phenotype_id = phenotype_id
        self.phenotype_title = phenotype_title
        self.confidence = confidence
        self.moi = moi
        self.submitter = submitter
