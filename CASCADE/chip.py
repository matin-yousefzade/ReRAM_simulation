import numpy as np
import pandas as pd
from time import time
import matplotlib.pyplot as plt
import math

BANDWIDTH = 8 * 25.6    # Gb/s
CYCLE_TIME = 25         # ns
CHIP_AREA = 7.514       # mm2
PEAK_COMPUTATIONAL_DENSITY = {8: 4360.926, 16: 1090.231}   # GOP/s/mm2

ENERGY = {}
ENERGY['DRAM'] = 20000                                # fJ
ENERGY['eDRAM'] = 84.228                              # fJ
ENERGY['IR'] = 60.546                                 # fJ
ENERGY['ADC'] = 1949.682                              # fJ
ENERGY['OR'] = 5.615                                  # fJ
ENERGY['DAC'] = 390.625                               # fJ
ENERGY['MAC_RRAM_read'] = 7500                        # fJ
ENERGY['MAC_RRAM_write'] = 3750000                    # fJ
ENERGY['buffer_RRAM_read'] = 1648                     # fJ
ENERGY['buffer_RRAM_write'] = 824000                  # fJ

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
    def __init__(self, apu_per_chip, cb_per_apu, cb_size, bit_per_cell):
        self.apu_per_chip = apu_per_chip
        self.cb_per_apu = cb_per_apu
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
        total_memory_cycles = 0
        cb_cycles = 0
        total_number_of_rewrites = 0
        total_DRAM_access = 0
        total_MAC_RRAM_write = 0
        start_finish = np.zeros([len(network_structure), 2])
        cb_per_chip = self.apu_per_chip * self.cb_per_apu

        for l in range(len(network_structure)):
            start_finish[l, 0] = total_cycles
            current_layer = network_structure.iloc[l]

            input_size = current_layer['H'] * current_layer['W'] * current_layer['C'] * bit_width
            weight_size = current_layer['M'] * current_layer['R'] * current_layer['S'] * current_layer['C'] * bit_width
            output_size = (current_layer['H'] // current_layer['Sx']) * (current_layer['W'] // current_layer['Sy']) * current_layer['M'] * bit_width

            if (current_layer['type'] != 'pool'):
                number_of_windows = (current_layer['H'] // current_layer['Sx']) * (current_layer['W'] // current_layer['Sy'])
                number_of_rows = math.ceil(current_layer['R'] * current_layer['S'] * current_layer['C'] / self.cb_size)
                number_of_cols = math.ceil(current_layer['M'] * bit_width / self.bit_per_cell / self.cb_size)
                cb_per_replicate = number_of_rows * number_of_cols

                if (cb_per_replicate <= cb_per_chip):
                    number_of_replicates = cb_per_chip // cb_per_replicate
                    number_of_rewrites = 1
                    cb_per_cycle = number_of_replicates * cb_per_replicate
                    compute_cycles = math.ceil(number_of_windows / number_of_replicates) * bit_width
                    total_MAC_RRAM_write += number_of_replicates * cb_per_replicate
                else:
                    number_of_rewrites = math.ceil(cb_per_replicate / cb_per_chip)
                    cb_per_cycle = cb_per_replicate / number_of_rewrites
                    compute_cycles = number_of_rewrites * number_of_windows * bit_width
                    total_MAC_RRAM_write += cb_per_replicate

                total_number_of_rewrites += number_of_rewrites
                cb_cycles += cb_per_cycle * compute_cycles
                memory_cycles = weight_size / (BANDWIDTH * CYCLE_TIME)
                total_cycles += compute_cycles + memory_cycles
                total_memory_cycles += memory_cycles
                total_DRAM_access += weight_size

            total_DRAM_access += input_size + output_size
            start_finish[l, 1] = total_cycles

        total_cycles = int(total_cycles)
        total_memory_cycles = int(total_memory_cycles)
        total_compute_cycles = total_cycles - total_memory_cycles
        latency = total_cycles
        memory_latency = total_memory_cycles
        memory_access_percentage = round(total_memory_cycles / total_cycles * 100, 3)
        real_utilization = cb_cycles / (cb_per_chip * total_cycles)
        ideal_utilization = cb_cycles / (cb_per_chip * total_compute_cycles)
        throughput = round(number_of_operations(network_address) / (latency * CYCLE_TIME), 3)
        computational_density = round(throughput / CHIP_AREA, 3)
        cd_error = calc_error(computational_density / real_utilization, PEAK_COMPUTATIONAL_DENSITY[bit_width])

        energy = {}
        energy['DRAM'] = total_DRAM_access * ENERGY['DRAM']
        energy['eDRAM'] = 2 * cb_cycles * self.cb_size * ENERGY['eDRAM']
        energy['IR'] = 2 * cb_cycles * self.cb_size * ENERGY['IR']
        energy['ADC'] = (cb_cycles // bit_width) * (self.cb_size * self.bit_per_cell / bit_width) * 10 * ENERGY['ADC']
        energy['OR'] = 2 * (cb_cycles // bit_width) * (self.cb_size * self.bit_per_cell) * ENERGY['OR']
        energy['DAC'] = cb_cycles * self.cb_size * ENERGY['DAC']
        energy['MAC_RRAM_read'] = cb_cycles * ENERGY['MAC_RRAM_read']
        energy['MAC_RRAM_write'] = total_MAC_RRAM_write * ENERGY['MAC_RRAM_write']
        energy['buffer_RRAM_read'] = 2 * (cb_cycles // bit_width) * ENERGY['buffer_RRAM_read']
        energy['buffer_RRAM_write'] = 2 * (cb_cycles // bit_width) * ENERGY['buffer_RRAM_write']

        total_energy = round(sum(list(energy.values())) * 1e-12, 3)
        energy_efficiency = round(number_of_operations(network_address) / total_energy * 1e-6, 3)

        if (plot):
            self.plot_energy(energy)
            self.plot_cycles(start_finish)

        return (latency, memory_latency, memory_access_percentage, round(real_utilization * 100, 3), round(ideal_utilization * 100, 3), throughput, computational_density, cd_error, total_energy, energy_efficiency, total_number_of_rewrites) + tuple(energy.values())

    def simulate(self, file_address, benchmarks, bit_width, plot):
        results = []
        for b in benchmarks:
            start_time = time()
            results.append(self.run(network_address='../benchmarks/' + b + '.csv', bit_width=bit_width, plot=plot))
            print(f'{b} simulation time: {round(time() - start_time, 3)} seconds.')
            print(results[-1])

        results.append(list(np.round(np.average(results, axis=0), 3)))
        metrics = ['latency', 'memory_latency', 'memory_access_percentage', 'real_utilization', 'ideal_utilization', 'throughput', 'computational_density', 'cd_error', 'energy', 'energy_efficiency', 'total_number_of_rewrites', 'DRAM', 'eDRAM', 'IR', 'ADC', 'OR', 'DAC', 'MAC_RRAM_read', 'MAC_RRAM_write', 'buffer_RRAM_read', 'buffer_RRAM_write']
        results = pd.DataFrame(results, columns=metrics)
        bm = benchmarks.copy()
        bm.append('AVG')
        results.insert(0, 'dnn', bm)
        results.set_index('dnn', inplace=True)
        results.to_csv(file_address)
