
class Logger(object):
    def __init__(self, name):
        self.name = name
    
    def printLog(self, text):
        print(self.format(text))

    def format(self, text):
        return '[' + self.name + '] ' + text