class Output_Buffer:
    def __init__(self, H, W, C):
        self.input_index = 0
        self.H = H
        self.W = W
        self.C = C
        self.input_memory_index = 0

    def is_full_input_memory(self):
        return (self.input_memory_index == self.H * self.W * self.C)

    def update_input_memory(self, x):
        self.input_memory_index += x

    def free_input_memory(self):
        self.input_memory_index = 0
