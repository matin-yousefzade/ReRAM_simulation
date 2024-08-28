import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

W = 0.17
ALPHA = 40
rcParams['font.weight'] = 'bold'

df_CASCADE = pd.read_csv('../results/CASCADE.csv')

number_of_inferences = 1 * 365 * 24 * 60 * 60 * 30
MAC_RRAM_rewrites = df_CASCADE['total_number_of_rewrites'] * number_of_inferences
buffer_RRAM_rewrites = np.subtract(df_CASCADE['latency'], df_CASCADE['memory_latency']) // 16 * number_of_inferences

x = list(df_CASCADE['dnn'])
x_axis = np.arange(len(x))

plt.figure(figsize=(8, 4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x_axis - W, MAC_RRAM_rewrites, 1.8 * W, label='MAC ReRAM', color='#BA1B01', edgecolor='black')
plt.text(len(x) - 1 - W, 1.05 * MAC_RRAM_rewrites[len(x) - 1], '{:.1e}'.format(MAC_RRAM_rewrites[len(x) - 1]), ha='center', rotation=ALPHA)

plt.bar(x_axis + W, buffer_RRAM_rewrites, 1.8 * W, label='Buffer ReRAM', color='#FFB400', edgecolor='black')
plt.text(len(x) - 1 + W, 1.02 * buffer_RRAM_rewrites[len(x) - 1], '{:.1e}'.format(buffer_RRAM_rewrites[len(x) - 1]), ha='center', rotation=ALPHA)

plt.xticks(x_axis, x)
plt.yscale('log')
plt.ylabel('Number of Writes', weight='bold')
plt.legend(loc='upper left')
plt.savefig('nws_writes.pdf', bbox_inches='tight')
plt.show()
