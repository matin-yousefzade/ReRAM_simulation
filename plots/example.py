import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.weight'] = 'bold'

plt.figure(figsize=(7,4))
ax = plt.axes()
ax.set_axisbelow(True)

data = {'1': 20, '2': 15, '3-1': 30, '3-2': 35, '4': 50}

layers = list(data.keys())
cycles = list(data.values())

plt.barh(layers, cycles, color='w')

plt.xlabel('Cycles', weight='bold')
plt.ylabel('Layers', weight='bold')
plt.xticks([])
plt.savefig('example.svg', bbox_inches='tight')
plt.show()
