import chip

benchmarks = ['AlexNet', 'VGG-11', 'VGG-16', 'VGG-19', 'MSRA-A', 'MSRA-B', 'MSRA-C']

ch = chip.Chip(tile_per_chip=115, ima_per_tile=8, cb_per_ima=4, cb_size=512, bit_per_cell=4)

# ch.simulate(file_address='../results/RAELLA_FF.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=False, pipelined=False, plot=False)
# ch.simulate(file_address='../results/RAELLA_TF.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=True, pipelined=False, plot=False)
# ch.simulate(file_address='../results/RAELLA_FT.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=False, pipelined=True, plot=False)
# ch.simulate(file_address='../results/RAELLA_TT.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=True, pipelined=True, plot=False)

print(ch.run(network_address='../benchmarks/' + benchmarks[2] + '.csv', number_of_chips=0, bit_width=16, overlapped=True, pipelined=True, plot=True))
