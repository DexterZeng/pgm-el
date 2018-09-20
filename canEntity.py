class canEntity(object):

    def __init__(self, name, rtf, rpm, mention_ID):
        self.name = name
        self.rtf = rtf
        self.rpm = rpm
        self.mention_ID = mention_ID

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_rtf(self):
        return self.rtf

    def get_rpm(self):
        return self.rpm

    def get_mention_ID(self):
        return self.mention_ID