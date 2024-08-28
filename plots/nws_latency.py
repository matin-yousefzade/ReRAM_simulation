import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

W = 0.22
ALPHA = 40
DIFF = 0.4
rcParams['font.weight'] = 'bold'

df_CASCADE = pd.read_csv('../results/CASCADE.csv')

x = list(df_CASCADE['dnn'])
x_axis = np.arange(len(x))

weight_movement_cycles = df_CASCADE['memory_latency'] / 1e6
computation_cycles = np.subtract(df_CASCADE['latency'], df_CASCADE['memory_latency']) / 1e6
computation_cycles[7] = weight_movement_cycles[7] / df_CASCADE['memory_access_percentage'][7] * 100 - weight_movement_cycles[7]

avg_wgh_mov_per = round(weight_movement_cycles[len(x) - 1] / (weight_movement_cycles[len(x) - 1] + computation_cycles[len(x) - 1]) * 100, 1)
avg_comp_per = round(computation_cycles[len(x) - 1] / (weight_movement_cycles[len(x) - 1] + computation_cycles[len(x) - 1]) * 100, 1)

plt.figure(figsize=(8, 4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x, weight_movement_cycles, 1.8 * W, label='Weight Movement', color='#BA1B01', edgecolor='black')
plt.text(len(x) - 1 - DIFF, 0.7 * weight_movement_cycles[len(x) - 1], f'{avg_wgh_mov_per}%', ha='center', rotation=ALPHA)

plt.bar(x, computation_cycles, 1.8 * W, bottom=weight_movement_cycles, label='Computation', color='#FFB400', edgecolor='black')
plt.text(len(x) - 1 - DIFF, weight_movement_cycles[len(x) - 1] + 0.45 * computation_cycles[len(x) - 1], f'{avg_comp_per}%', ha='center', rotation=ALPHA)

plt.xticks(x_axis, x)
plt.ylabel('Latency (Million Cycles)', weight='bold')
plt.legend()
plt.savefig('nws_latency.pdf', bbox_inches='tight')
plt.show()
