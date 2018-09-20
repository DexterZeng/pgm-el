class Mention(object):
    # id refers to the mention ID within a document
    def __init__(self, id, name, trueEn):
        self.id = id
        self.name = name
        self.trueEn = trueEn

    def set_name(self, name):
        self.name = name

    def set_trueEn(self, trueEn):
        self.trueEn = trueEn

    def get_name(self):
        return self.name

    def get_trueEn(self):
        return self.trueEn

    def get_id(self):
        return self.id
