import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

W = 0.17
ALPHA = 40
rcParams['font.weight'] = 'bold'

df_CASCADE = pd.read_csv('../results/CASCADE.csv')

x = list(df_CASCADE['dnn'])
x_axis = np.arange(len(x))

plt.figure(figsize=(8,4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x_axis - W, df_CASCADE['real_utilization'], 1.8 * W, label='Real Utilization', color='#BA1B01', edgecolor='black')
plt.text(len(x) - 1 - W, 1.05 * df_CASCADE['real_utilization'][len(x) - 1], round(df_CASCADE['real_utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis + W, df_CASCADE['ideal_utilization'], 1.8 * W, label='Ideal Utilization', color='#FFB400', edgecolor='black')
plt.text(len(x) - 1 + W, 1.02 * df_CASCADE['ideal_utilization'][len(x) - 1], round(df_CASCADE['ideal_utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.xticks(x_axis, x)
plt.yticks(np.arange(0, 110, 10))
plt.ylabel('Utilization (%)', weight='bold')
plt.legend(loc='upper left')
plt.savefig('nws_util.pdf', bbox_inches='tight')
plt.show()
