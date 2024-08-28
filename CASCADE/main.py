import chip

benchmarks = ['AlexNet', 'VGG-11', 'VGG-16', 'VGG-19', 'MSRA-A', 'MSRA-B', 'MSRA-C']

ch = chip.Chip(apu_per_chip=80, cb_per_apu=80, cb_size=64, bit_per_cell=1)

ch.simulate(file_address='../results/CASCADE.csv', benchmarks=benchmarks, bit_width=16, plot=True)

#print(ch.run(network_address='../benchmarks/' + benchmarks[2] + '.csv', bit_width=16, plot=True))
