class GenomicEntityPrediseasePair:
    def __init__(
        self,
        hgnc_id: str,
        hgnc_symbol: str,
        gene_other_ids: list,
        gene_alias: str,
        mondo_id: str,
        predisease_other_ids: list,
        predisease_title: str,
        predisease_alias: str,
        confidence: str,
        moi: str,
        pmids: list,
        submitter: str,
        evaluation_date: str,
        submission_date: str,
    ):
        self.hgnc_id = hgnc_id
        self.hgnc_symbol = hgnc_symbol
        self.gene_other_ids = gene_other_ids
        self.gene_alias = gene_alias
        self.mondo_id = mondo_id
        self.predisease_other_ids = predisease_other_ids
        self.predisease_title = predisease_title
        self.predisease_alias = predisease_alias
        self.confidence = confidence
        self.moi = moi
        self.pmids = pmids
        self.submitter = submitter
        self.evaluation_date = evaluation_date
        self.submission_date = submission_date
