import chip

benchmarks = ['AlexNet', 'VGG-11', 'VGG-16', 'VGG-19', 'MSRA-A', 'MSRA-B', 'MSRA-C']

ch = chip.Chip(tile_per_chip=128, ima_per_tile=9, cu_per_ima=64, cb_size=64, bit_per_cell=1)

ch.simulate(file_address='../results/ResPIM.csv', benchmarks=benchmarks, bit_width=16, plot=True)

#print(ch.run(network_address='../benchmarks/' + benchmarks[2] + '.csv', bit_width=16, plot=True))
