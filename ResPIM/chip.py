import numpy as np
import pandas as pd
from time import time
import matplotlib.pyplot as plt
import math

CYCLE_TIME = 100        # ns
CHIP_AREA = 90.965      # mm2
PEAK_COMPUTATIONAL_DENSITY = {8: 4149.808, 16: 1037.452}      # GOP/s/mm2

ENERGY = {}
ENERGY['eDRAM'] = 84.56                               # fJ
ENERGY['tile_OR'] = 60.546                            # fJ
ENERGY['IR'] = 5.615                                  # fJ
ENERGY['DAC'] = 390.625                               # fJ
ENERGY['ADC'] = 1859.936                              # fJ
ENERGY['IMA_OR'] = 5.615                              # fJ
ENERGY['weight_memory'] = 0.458                       # fJ
ENERGY['configuration_array'] = 5.615                 # fJ
ENERGY['CB'] = 30000                                  # fJ
ENERGY['SH'] = 0.976                                  # fJ

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
    def __init__(self, tile_per_chip, ima_per_tile, cu_per_ima, cb_size, bit_per_cell):
        self.tile_per_chip = tile_per_chip
        self.ima_per_tile = ima_per_tile
        self.cu_per_ima = cu_per_ima
        self.cb_size = cb_size
        self.bit_per_cell = bit_per_cell

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

    def run(self, network_address, bit_width, plot):
        network_structure = pd.read_csv(network_address, names=['type', 'H', 'W', 'C', 'R', 'S', 'M', 'Sx', 'Sy'])

        total_cycles = 0
        ima_cycles = 0
        total_number_of_rewrites = 0
        total_ima_rewrites = 0
        start_finish = np.zeros([len(network_structure), 2])
        ima_per_chip = self.tile_per_chip * self.ima_per_tile

        for l in range(len(network_structure)):
            start_finish[l, 0] = total_cycles
            current_layer = network_structure.iloc[l]

            if (current_layer['type'] != 'pool'):
                number_of_windows = (current_layer['H'] // current_layer['Sx']) * (current_layer['W'] // current_layer['Sy'])
                number_of_rows = math.ceil(current_layer['R'] * current_layer['S'] * current_layer['C'] / self.cb_size)
                number_of_cols = math.ceil(current_layer['M'] / self.cu_per_ima)
                ima_per_replicate = number_of_rows * number_of_cols

                if (ima_per_replicate <= ima_per_chip):
                    number_of_replicates = ima_per_chip // ima_per_replicate
                    number_of_rewrites = 1
                    total_ima_rewrites += number_of_replicates * ima_per_replicate
                    ima_per_cycle = number_of_replicates * ima_per_replicate
                    cycles = math.ceil(number_of_windows / number_of_replicates)
                else:
                    number_of_rewrites = math.ceil(ima_per_replicate / ima_per_chip)
                    total_ima_rewrites += ima_per_replicate
                    ima_per_cycle = ima_per_replicate / number_of_rewrites
                    cycles = number_of_rewrites * number_of_windows

                total_number_of_rewrites += number_of_rewrites
                ima_cycles += ima_per_cycle * cycles
                total_cycles += cycles + number_of_rewrites

            start_finish[l, 1] = total_cycles

        latency = total_cycles
        utilization = ima_cycles / (ima_per_chip * total_cycles)
        throughput = round(number_of_operations(network_address) / (latency * CYCLE_TIME), 3)
        computational_density = round(throughput / CHIP_AREA, 3)
        cd_error = calc_error(computational_density / utilization, PEAK_COMPUTATIONAL_DENSITY[bit_width])

        energy = {}
        energy['eDRAM'] = 2 * ima_cycles * self.cb_size * bit_width * ENERGY['eDRAM']
        energy['tile_OR'] = 2 * ima_cycles * self.cu_per_ima * bit_width * ENERGY['tile_OR']
        energy['IR'] = 2 * ima_cycles * self.cb_size * bit_width * ENERGY['IR']
        energy['DAC'] = ima_cycles * self.cb_size * bit_width * ENERGY['DAC']
        energy['ADC'] = ima_cycles * self.cu_per_ima * 10 * ENERGY['ADC']
        energy['IMA_OR'] = 2 * ima_cycles * self.cu_per_ima * bit_width * ENERGY['IMA_OR']
        energy['weight_memory'] = total_ima_rewrites * self.cu_per_ima * self.cb_size * bit_width * ENERGY['weight_memory']
        energy['configuration_array'] = total_ima_rewrites * self.cu_per_ima * self.cb_size * bit_width * ENERGY['configuration_array']
        energy['CB'] = ima_cycles * self.cu_per_ima * ENERGY['CB']
        energy['SH'] = ima_cycles * self.cu_per_ima * 31 * ENERGY['SH']

        total_energy = round(sum(list(energy.values())) * 1e-12, 3)
        energy_efficiency = round(number_of_operations(network_address) / total_energy * 1e-6, 3)
        power = round(total_energy / (latency * CYCLE_TIME) * 1e6, 3)

        if (plot):
            self.plot_energy(energy)
            self.plot_cycles(start_finish)

        return (latency, round(utilization * 100, 3), throughput, computational_density, cd_error, total_energy, energy_efficiency, power, total_number_of_rewrites) + tuple(energy.values())

    def simulate(self, file_address, benchmarks, bit_width, plot):
        results = []
        for b in benchmarks:
            start_time = time()
            results.append(self.run(network_address='../benchmarks/' + b + '.csv', bit_width=bit_width, plot=plot))
            print(f'{b} simulation time: {round(time() - start_time, 3)} seconds.')
            print(results[-1])

        results.append(list(np.round(np.average(results, axis=0), 3)))
        metrics = ['latency', 'utilization', 'throughput', 'computational_density', 'cd_error', 'energy', 'energy_efficiency', 'power',
                   'total_number_of_rewrites', 'eDRAM', 'tile_OR', 'IR', 'DAC', 'ADC', 'IMA_OR', 'weight_memory', 'configuration_array', 'CB', 'SH']
        results = pd.DataFrame(results, columns=metrics)
        bm = benchmarks.copy()
        bm.append('AVG')
        results.insert(0, 'dnn', bm)
        results.set_index('dnn', inplace=True)
        results.to_csv(file_address)
