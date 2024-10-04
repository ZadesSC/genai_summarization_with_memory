import sys

class Tee:
    def __init__(self, output_file):
        self.terminal = sys.stdout
        self.log = open(output_file, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()