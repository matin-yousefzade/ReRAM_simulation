import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import layer
import output_buffer

CYCLE_TIME = 100    # ns
CHIP_AREA = 84.7    # mm2
PEAK_COMPUTATIONAL_DENSITY = {8 : 1948, 16 : 487}   # GOP/s/mm2

def number_of_operations(network_address):
    network_details = pd.read_csv(network_address, names=['type', 'H', 'W', 'C', 'R', 'S', 'M', 'Sx', 'Sy'])

    number_of_operations = 0
    for l in range(len(network_details)):
        if(network_details.loc[l, 'type'] != 'pool'):
            E = network_details.loc[l, 'H'] // network_details.loc[l, 'Sx']
            F = network_details.loc[l, 'W'] // network_details.loc[l, 'Sy']
            filter_size = network_details.loc[l, 'R'] * network_details.loc[l, 'S'] * network_details.loc[l, 'C']
            number_of_operations +=  E * F * network_details.loc[l, 'M'] * filter_size * 2

    return number_of_operations

class Chip:
    def __init__(self, tile_per_chip, ima_per_tile, cb_per_ima, cb_size, input_width, weight_width, bit_per_cell):
        self.tile_per_chip = tile_per_chip
        self.ima_per_tile = ima_per_tile
        self.cb_per_ima = cb_per_ima
        self.cb_size = cb_size
        self.input_width = input_width
        self.weight_width = weight_width
        self.bit_per_cell = bit_per_cell

    def calc_error(self, x, y):
        return round(abs(x - y) / y * 100, 3)

    def map_weights(self, network_address):
        network_details = pd.read_csv(network_address, names=['type', 'H', 'W', 'C', 'R', 'S', 'M', 'Sx', 'Sy'])
        network_details['cb_per_replicate'] = len(network_details) * [0]
        network_details['replication_coefficient'] = len(network_details) * [0]
        network_details['number_of_replicates'] = len(network_details) * [0]

        replication_coefficient = 1
        for l in range(len(network_details)):
            if(network_details.loc[l, 'type'] != 'pool'):
                number_of_rows = math.ceil(network_details.loc[l, 'R'] * network_details.loc[l, 'S'] * network_details.loc[l, 'C'] / self.cb_size)
                number_of_cols = math.ceil(network_details.loc[l, 'M'] * self.weight_width / self.bit_per_cell / self.cb_size)
                cb_per_replicate = number_of_rows * number_of_cols
                network_details.loc[l, 'cb_per_replicate'] = cb_per_replicate
                network_details.loc[l, 'replication_coefficient'] = replication_coefficient

            replication_coefficient *= network_details.loc[l, 'Sx'] * network_details.loc[l, 'Sy']

        minimum_required_cb = 0
        for l in range(len(network_details)):
            if (network_details.loc[l, 'type'] != 'pool'):
                network_details.loc[l, 'number_of_replicates'] = 1
                minimum_required_cb += network_details.loc[l, 'cb_per_replicate']

        cb_per_chip = self.tile_per_chip * self.ima_per_tile * self.cb_per_ima
        minimum_required_chips = math.ceil(minimum_required_cb / cb_per_chip)
        total_cb = minimum_required_chips * cb_per_chip - minimum_required_cb
        minimum_cb_per_replicate = network_details[network_details['cb_per_replicate'] > 0].min()['cb_per_replicate']
        
        i = 1
        while(total_cb >= minimum_cb_per_replicate):
            for l in range(len(network_details)):
                if(network_details.loc[l, 'type'] != 'pool'):
                    if(i % network_details.loc[l, 'replication_coefficient'] == 0):
                        if(total_cb >= network_details.loc[l, 'cb_per_replicate']):
                            network_details.loc[l, 'number_of_replicates'] += 1
                            total_cb -= network_details.loc[l, 'cb_per_replicate']
            i += 1

        return network_details, minimum_required_chips

    def plot_cycles(self, start_finish, resources):
        new_start_finish = start_finish.copy()
        for i in range(len(start_finish)):
            for j in range(1, len(start_finish[i])):
                new_start_finish[i, j] = np.max([start_finish[i, j] - start_finish[i, j - 1], int(0.005 * np.max(start_finish))])

        pd.DataFrame(new_start_finish).plot(kind='barh', stacked=True, color=['w', 'r', 'w', 'g', 'w', 'b', 'w', 'm'], legend=False)

        for i in range(len(resources)):
            plt.text(1.1 * np.max(start_finish), i - 0.2, f'{resources[i]}%', ha='center', fontsize=8)

        plt.xlim(0, 1.2 * np.max(start_finish))
        plt.xlabel('Cycles')
        plt.ylabel('Layers')
        plt.show()

    def run(self, network_address, overlapped, pipelined, batch_size, plot):
        network_details, minimum_required_chips = self.map_weights(network_address)

        layers = []
        for l in range(len(network_details)):
            layers.append(layer.Layer(layer_index=l, layer_details=network_details.loc[l], input_width=self.input_width))

        ob = output_buffer.Output_Buffer(H=layers[-1].E, W=layers[-1].F, C=layers[-1].M)

        cycles = 0
        total_cb_cycles = 0
        start_finish = -1 * np.ones([len(network_details), 2 * batch_size])

        while(True):
            for l in range(len(layers) - 1, -1, -1):
                cb_cycles = layers[l].run(layers, ob, overlapped)
                total_cb_cycles += cb_cycles
                if(start_finish[l, 2 * layers[l].input_index] == -1 and cb_cycles > 0):
                    start_finish[l, 2 * layers[l].input_index] = cycles - 1

            cycles += 1

            for l in range(len(network_details) - 1):
                if(start_finish[l, 2 * layers[l].input_index + 1] == -1):
                    if(layers[l].input_index == layers[l + 1].input_index):
                        if(layers[l + 1].is_full_input_memory()):
                            start_finish[l, 2 * layers[l].input_index + 1] = cycles
                            if(layers[l].input_index < batch_size - 1):
                                if(pipelined):
                                    layers[l].input_index += 1
                                    layers[l].free_input_memory()

            if (start_finish[-1, 2 * layers[-1].input_index + 1] == -1):
                if (layers[-1].input_index == ob.input_index):
                    if (ob.is_full_input_memory()):
                        start_finish[-1, 2 * layers[-1].input_index + 1] = cycles
                        if (layers[-1].input_index < batch_size - 1):
                            layers[-1].input_index += 1
                            layers[-1].free_input_memory()
                            ob.input_index += 1
                            ob.free_input_memory()
                            if(pipelined == False):
                                for l in range(len(layers) - 1):
                                    layers[l].input_index += 1
                                    layers[l].free_input_memory()
                        else:
                            break

        total_cb = minimum_required_chips * self.tile_per_chip * self.ima_per_tile * self.cb_per_ima
        latency = start_finish[-1, 3] - start_finish[0, 2]
        pipeline_cycle_time = start_finish[-1, 5] - start_finish[-1, 3]
        utilization = (total_cb_cycles / batch_size) / (total_cb * pipeline_cycle_time)
        throughput = round(number_of_operations(network_address) / (pipeline_cycle_time * CYCLE_TIME), 3)
        computational_density = round(throughput / (minimum_required_chips * CHIP_AREA), 3)
        error = self.calc_error(computational_density / utilization, PEAK_COMPUTATIONAL_DENSITY[self.weight_width])

        if(plot):
            resources = np.multiply(network_details['number_of_replicates'], network_details['cb_per_replicate'])
            resources = round(resources / np.sum(resources) * 100, 1)
            self.plot_cycles(start_finish, resources)

        return cycles, latency, pipeline_cycle_time, round(utilization * 100, 3), throughput, computational_density, error, minimum_required_chips
