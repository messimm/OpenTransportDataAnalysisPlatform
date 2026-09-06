class BasicChecker:
    def __init__(self, cfg=None):
        self.cfg = cfg or {}

    def check(self, data):
        return True

    def checkFilter(self, data):
        return data
