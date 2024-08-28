import numpy as np
import pandas as pd
from time import time
import matplotlib.pyplot as plt
import math
import layer
import output_buffer

CYCLE_TIME = 100        # ns
CHIP_AREA = 85.283      # mm2
PEAK_COMPUTATIONAL_DENSITY = {8 : 1936.502, 16 : 484.125}   # GOP/s/mm2

ENERGY_POWER = {}
ENERGY_POWER['hyper_transport'] = 10400     # mW
ENERGY_POWER['router'] = 10.5               # mW
ENERGY_POWER['eDRAM'] = 84.228              # fJ
ENERGY_POWER['eDRAM_bus'] = 56.966          # fJ
ENERGY_POWER['tile_SA'] = 52.083            # fJ
ENERGY_POWER['tile_OR'] = 54.687            # fJ
ENERGY_POWER['IR'] = 60.546                 # fJ
ENERGY_POWER['IMA_SA'] = 156.25             # fJ
ENERGY_POWER['IMA_OR'] = 5.615              # fJ
ENERGY_POWER['DAC'] = 390.625               # fJ
ENERGY_POWER['CB'] = 30000                  # fJ
ENERGY_POWER['SH'] = 0.976                  # fJ
ENERGY_POWER['ADC'] = 1562.5                # fJ

def calc_error(x, y):
    return round(abs(x - y) / y * 100, 3)

def number_of_operations(network_address):
    network_details = pd.read_csv(network_address, names=['type', 'H', 'W', 'C', 'R', 'S', 'M', 'Sx', 'Sy'])

    number_of_operations = 0
    for l in range(len(network_details)):
        if(network_details.loc[l, 'type'] != 'pool'):
            E = network_details.loc[l, 'H'] // network_details.loc[l, 'Sx']
            F = network_details.loc[l, 'W'] // network_details.loc[l, 'Sy']
            filter_size = network_details.loc[l, 'R'] * network_details.loc[l, 'S'] * network_details.loc[l, 'C']
            number_of_operations += E * F * network_details.loc[l, 'M'] * filter_size * 2

    return number_of_operations

class Chip:
    def __init__(self, tile_per_chip, ima_per_tile, cb_per_ima, cb_size, bit_per_cell):
        self.tile_per_chip = tile_per_chip
        self.ima_per_tile = ima_per_tile
        self.cb_per_ima = cb_per_ima
        self.cb_size = cb_size
        self.bit_per_cell = bit_per_cell

    def map_weights(self, network_address, number_of_chips, bit_width):
        network_details = pd.read_csv(network_address, names=['type', 'H', 'W', 'C', 'R', 'S', 'M', 'Sx', 'Sy'])
        network_details['cb_per_replicate'] = len(network_details) * [0]
        network_details['replication_coefficient'] = len(network_details) * [0]
        network_details['number_of_replicates'] = len(network_details) * [0]

        replication_coefficient = 1
        for l in range(len(network_details)):
            if(network_details.loc[l, 'type'] != 'pool'):
                number_of_rows = math.ceil(network_details.loc[l, 'R'] * network_details.loc[l, 'S'] * network_details.loc[l, 'C'] / self.cb_size)
                number_of_cols = math.ceil(network_details.loc[l, 'M'] * bit_width / self.bit_per_cell / self.cb_size)
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
        minimum_required_chips = math.ceil(minimum_required_cb / cb_per_chip) if (number_of_chips == 0) else number_of_chips
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

    def plot_cycles(self, start_finish):
        plt.barh(range(len(start_finish)), start_finish[:, 1] - start_finish[:, 0], left=start_finish[:, 0])
        plt.xlabel('Cycles')
        plt.ylabel('Layers')
        plt.show()

    def plot_energy(self, energy):
        keys = list(energy.keys())
        values = list(energy.values())
        sorted_value_index = np.argsort(values)
        sorted_energy = {keys[i]: values[i] for i in sorted_value_index}
        plt.pie(list(sorted_energy.values()), labels=list(sorted_energy.keys()))
        plt.show()

    def find_cycle_per_inference(self, start_finish):
        cycle_per_inference = 0
        for l in range(len(start_finish)):
            if(l < (len(start_finish) - 1)):
                temp = start_finish[l + 1, 1] - start_finish[l, 0]
            else:
                temp = start_finish[l, 1] - start_finish[l, 0]

            cycle_per_inference = np.max([cycle_per_inference, temp])

        return cycle_per_inference

    def run(self, network_address, number_of_chips, bit_width, overlapped, pipelined, plot):
        network_details, minimum_required_chips = self.map_weights(network_address, number_of_chips, bit_width)
        #print(network_details[['replication_coefficient', 'number_of_replicates', 'cb_per_replicate']])
        layers = []
        for l in range(len(network_details)):
            layers.append(layer.Layer(layer_index=l, layer_details=network_details.loc[l], bit_width=bit_width))

        ob = output_buffer.Output_Buffer(H=layers[-1].E, W=layers[-1].F, C=layers[-1].M)

        cycles = 0
        total_cb_cycles = 0
        start_finish = -1 * np.ones([len(network_details), 2])

        while(True):
            for l in range(len(layers) - 1, -1, -1):
                cb_cycles = layers[l].run(layers, ob, overlapped)
                total_cb_cycles += cb_cycles
                if(start_finish[l, 0] == -1 and cb_cycles > 0):
                    start_finish[l, 0] = cycles - 1

            cycles += 1

            for l in range(len(network_details) - 1):
                if(start_finish[l, 1] == -1 and layers[l + 1].is_full_input_memory()):
                    start_finish[l, 1] = cycles

            if(ob.is_full_input_memory()):
                start_finish[-1, 1] = cycles
                break

        total_cb = minimum_required_chips * self.tile_per_chip * self.ima_per_tile * self.cb_per_ima
        latency = cycles
        cycle_per_inference = self.find_cycle_per_inference(start_finish) if pipelined else cycles
        utilization = total_cb_cycles / (total_cb * cycle_per_inference)
        throughput = round(number_of_operations(network_address) / (cycle_per_inference * CYCLE_TIME), 3)
        computational_density = round(throughput / (minimum_required_chips * CHIP_AREA), 3)
        cd_error = calc_error(computational_density / utilization, PEAK_COMPUTATIONAL_DENSITY[bit_width])

        energy = {}
        energy['hyper_transport'] = minimum_required_chips * ENERGY_POWER['hyper_transport'] * cycle_per_inference * CYCLE_TIME * utilization * 1e3
        energy['router'] = minimum_required_chips * self.tile_per_chip * ENERGY_POWER['router'] * cycle_per_inference * CYCLE_TIME * utilization * 1e3
        energy['eDRAM'] = 2 * total_cb_cycles * self.cb_size * ENERGY_POWER['eDRAM']
        energy['eDRAM_bus'] = total_cb_cycles * self.cb_size * ENERGY_POWER['eDRAM_bus']
        energy['tile_SA'] = (total_cb_cycles // bit_width) * (self.cb_size * self.bit_per_cell // bit_width) * ENERGY_POWER['tile_SA']
        energy['tile_OR'] = 2 * (total_cb_cycles // bit_width) * (self.cb_size * self.bit_per_cell) * ENERGY_POWER['tile_OR']
        energy['IR'] = 2 * total_cb_cycles * self.cb_size * ENERGY_POWER['IR']
        energy['IMA_SA'] = total_cb_cycles * (self.cb_size * self.bit_per_cell // bit_width) * ENERGY_POWER['IMA_SA']
        energy['IMA_OR'] = 2 * total_cb_cycles * (self.cb_size * self.bit_per_cell) * ENERGY_POWER['IMA_OR']
        energy['DAC'] = total_cb_cycles * self.cb_size * ENERGY_POWER['DAC']
        energy['CB'] = total_cb_cycles * ENERGY_POWER['CB']
        energy['SH'] = total_cb_cycles * self.cb_size * ENERGY_POWER['SH']
        energy['ADC'] = total_cb_cycles * self.cb_size * ENERGY_POWER['ADC']

        total_energy = round(sum(list(energy.values())) * 1e-12, 3)
        energy_efficiency = round(number_of_operations(network_address) / total_energy * 1e-6, 3)

        if(plot):
            self.plot_energy(energy)
            self.plot_cycles(start_finish)

        return (latency, cycle_per_inference, round(utilization * 100, 3), throughput, computational_density, cd_error, total_energy, energy_efficiency, minimum_required_chips) + tuple(energy.values())

    def simulate(self, file_address, benchmarks, number_of_chips, bit_width, overlapped, pipelined, plot):
        results = []
        for b in benchmarks:
            start_time = time()
            results.append(self.run(network_address='../benchmarks/' + b + '.csv', number_of_chips=number_of_chips, bit_width=bit_width, overlapped=overlapped, pipelined=pipelined, plot=plot))
            print(f'{b} simulation time: {round(time() - start_time, 3)} seconds.')
            print(results[-1])

        results.append(list(np.round(np.average(results, axis=0), 3)))
        metrics = ['latency', 'cycle_per_inference', 'utilization', 'throughput', 'computational_density', 'cd_error', 'energy', 'energy_efficiency', 'minimum_required_chips', 'hyper_transport', 'router', 'eDRAM', 'eDRAM_bus', 'tile_SA', 'tile_OR', 'IR', 'IMA_SA', 'IMA_OR', 'DAC', 'CB', 'SH', 'ADC']
        results = pd.DataFrame(results, columns=metrics)
        bm = benchmarks.copy()
        bm.append('AVG')
        results.insert(0, 'dnn', bm)
        results.set_index('dnn', inplace=True)
        results.to_csv(file_address)
