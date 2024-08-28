class Pipeline:
    def __init__(self, bit_width):
        self.bit_width = bit_width
        self.pipeline_length = bit_width + 5
        self.pipeline = self.pipeline_length * [0]

    def is_utilized(self):
        return (sum(self.pipeline[0 : self.bit_width]) > 0)

    def is_ready(self):
        return (sum(self.pipeline[0 : self.bit_width - 1]) == 0)

    def run(self, input):
        output = self.pipeline[-1]

        for i in range(self.pipeline_length - 1, 0, -1):
            self.pipeline[i] = self.pipeline[i - 1]

        self.pipeline[0] = input

        return output
