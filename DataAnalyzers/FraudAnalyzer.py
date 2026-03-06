import pandas as pd

from .BasicAnalyzer import BasicDataAnalysisModule


class PotentialFraudAnalysis(BasicDataAnalysisModule):
    def __init__(self, cfg):
        self.thr = cfg.get("threshold", 3)
        self.ticket_id = cfg.get("ticket_id", 1520)

    def analyze(self, data_loader, data_checker):
        if not hasattr(data_loader, "getDataByTimeRange"):
            raise AttributeError("PotentialFraudAnalysis requires loader method getDataByTimeRange")

        school = data_loader.getDataByColumnValue(None, "type_ticket", self.ticket_id)
        school = school[["ts", "id_vest", "number_ticket"]]

        cand_1 = (
            data_loader.getDataByTimeRange(
                school,
                pd.to_datetime("09:00:00").time(),
                pd.to_datetime("11:00:00").time(),
            )
            .groupby(["number_ticket"])
            .count()
        )
        cand_2 = (
            data_loader.getDataByTimeRange(
                school,
                pd.to_datetime("17:00:00").time(),
                pd.to_datetime("19:00:00").time(),
            )
            .groupby(["number_ticket"])
            .count()
        )

        cand_1 = cand_1[cand_1["ts"] > self.thr]
        cand_2 = cand_2[cand_2["ts"] > self.thr]

        all_candidates = len(school["number_ticket"].unique())
        final_candidates = list(cand_1.index.intersection(cand_2.index))
        ratio = len(final_candidates) / all_candidates if all_candidates else 0

        suspect = school[school["number_ticket"].isin(final_candidates)]
        return suspect, ([ratio, 1 - ratio], ["Suspect", "Normal"])
