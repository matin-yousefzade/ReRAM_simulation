import pipeline

class Layer:
    def __init__(self, layer_index, layer_details, bit_width):
        self.layer_index = layer_index
        self.type = layer_details['type']
        self.H = layer_details['H']
        self.W = layer_details['W']
        self.C = layer_details['C']
        self.R = layer_details['R']
        self.S = layer_details['S']
        self.M = layer_details['M']
        self.Sx = layer_details['Sx']
        self.Sy = layer_details['Sy']
        self.cb_per_replicate = layer_details['cb_per_replicate']
        self.replication_coefficient = layer_details['replication_coefficient']
        self.number_of_replicates = layer_details['number_of_replicates']
        self.E = self.H // self.Sx
        self.F = self.W // self.Sy
        self.input_memory_index = 0
        self.output_memory_index = 0
        self.pipelines = []
        for p in range(self.number_of_replicates):
            self.pipelines.append(pipeline.Pipeline(bit_width))
        if(self.layer_index == 0):
            self.input_memory_index = self.H * self.W * self.C

    def is_full_input_memory(self):
        return (self.input_memory_index == self.H * self.W * self.C)

    def update_input_memory(self, x):
        self.input_memory_index += x

    def memory_check(self):
        number_of_ready_windows = 0
        output_memory_index = self.output_memory_index // self.M

        while (output_memory_index < self.E * self.F):
            e = output_memory_index // self.F
            f = output_memory_index % self.F
            h = e * self.Sx
            w = f * self.Sy
            h += self.R - 1
            w += self.S - 1
            if (h >= self.H):
                h = self.H - 1
            if (w >= self.W):
                w = self.W - 1

            requested_input_memory_index = h * self.W * self.C + w * self.C + self.C - 1

            if (requested_input_memory_index < self.input_memory_index):
                number_of_ready_windows += 1
                output_memory_index += 1
                if (self.type != 'pool' and number_of_ready_windows == self.number_of_replicates):
                    break
            else:
                break

        return number_of_ready_windows

    def run(self, layers, output_buffer, overlapped):
        if(overlapped == False and self.is_full_input_memory() == False):
            return 0

        number_of_ready_windows = self.memory_check()

        cb_cycles = 0
        outputs = 0
        if(self.type != 'pool'):
            for p in range(self.number_of_replicates):
                if(self.pipelines[p].is_utilized()):
                    cb_cycles += self.cb_per_replicate

                if(number_of_ready_windows > 0 and self.pipelines[p].is_ready()):
                    outputs += self.pipelines[p].run(self.M)
                    self.output_memory_index += self.M
                    number_of_ready_windows -= 1
                else:
                    outputs += self.pipelines[p].run(0)

        else:
            self.output_memory_index += number_of_ready_windows * self.M
            cb_cycles = number_of_ready_windows * 1e-15
            outputs = number_of_ready_windows * self.M

        if (self.layer_index < len(layers) - 1):
            layers[self.layer_index + 1].update_input_memory(outputs)
        else:
            output_buffer.update_input_memory(outputs)

        return cb_cycles
