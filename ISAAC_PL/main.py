import chip

benchmarks = ['AlexNet', 'VGG-16', 'VGG-19', 'MSRA-19', 'MSRA-22', 'GoogleNet', 'ResNet-18', 'ResNet-50', 'SqueezeNet']

ch = chip.Chip(tile_per_chip=168, ima_per_tile=12, cb_per_ima=8, cb_size=128, input_width=16, weight_width=16, bit_per_cell=2)

print(ch.run(network_address='../benchmarks/' + benchmarks[4] + '.csv', overlapped=True, pipelined=True, batch_size=4, plot=True))
