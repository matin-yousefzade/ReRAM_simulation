import chip

benchmarks = ['AlexNet', 'VGG-11', 'VGG-16', 'VGG-19', 'MSRA-A', 'MSRA-B', 'MSRA-C']

ch = chip.Chip(tile_per_chip=168, ima_per_tile=12, cb_per_ima=8, cb_size=128, bit_per_cell=2)

# ch.simulate(file_address='../results/ISAAC_FF.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=False, pipelined=False, plot=False)
# ch.simulate(file_address='../results/ISAAC_TF.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=True, pipelined=False, plot=False)
# ch.simulate(file_address='../results/ISAAC_FT.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=False, pipelined=True, plot=False)
# ch.simulate(file_address='../results/ISAAC_TT.csv', benchmarks=benchmarks, number_of_chips=0, bit_width=16, overlapped=True, pipelined=True, plot=False)

print(ch.run(network_address='../benchmarks/' + benchmarks[2] + '.csv', number_of_chips=0, bit_width=16, overlapped=True, pipelined=True, plot=True))
