from .BasicAnalyzer import BasicDataAnalysisModule

class PotentialFraudAnalysis(BasicDataAnalysisModule):
	def __init__(self, cfg):
		self.thr = cfg.get("threshold", 3)
		self.ticket_id = cfg.get("ticket_id", 1520)
	def analyze(data_loader, data_checker):
		school = d.getDataByColumnValue(None, 'type_ticket', self.ticket_id)
		school = school[["ts", "id_vest", "number_ticket"]]
		cand_1 = d.getDataByTimeRange(school, pd.to_datetime("09:00:00").time(), pd.to_datetime("11:00:00").time()).groupby(["number_ticket"]).count()
		cand_2 = d.getDataByTimeRange(school, pd.to_datetime("17:00:00").time(), pd.to_datetime("19:00:00").time()).groupby(["number_ticket"]).count()
		cand_1 = cand_1[cand_1["ts"]>self.thr]
		cand_2 = cand_2[cand_2["ts"]>self.thr]
		all_cands = len(school['number_ticket'].unique())
		final_cands = list(cand_1.index.intersection(cand_2.index))
		ratio = len(final_cands)/all_cands
		suspect = school[school["number_ticket"].isin(final_cands)]
		return (suspect, ([ratio, 1-ratio], ["Suspect", "Normal"]))