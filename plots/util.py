import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

W = 0.1
ALPHA = 50
rcParams['font.weight'] = 'bold'

df_ISAAC = pd.read_csv('../results/ISAAC_TT.csv')
df_CASCADE = pd.read_csv('../results/CASCADE.csv')
df_RAELLA = pd.read_csv('../results2/RAELLA_TT.csv')
df_ResPIM = pd.read_csv('../results/ResPIM.csv')

x = list(df_ISAAC['dnn'])
x_axis = np.arange(len(x))

plt.figure(figsize=(8, 4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x_axis - 3 * W, df_ISAAC['utilization'], 1.8 * W, label='ISAAC', color='#0060FF', edgecolor='black')
plt.text(len(x) - 1 - 3 * W, 1.05 * df_ISAAC['utilization'][len(x) - 1], round(df_ISAAC['utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis - W, df_CASCADE['real_utilization'], 1.8 * W, label='CASCADE', color='#BA1B01', edgecolor='black')
plt.text(len(x) - 1 - W, 1.2 * df_CASCADE['real_utilization'][len(x) - 1], round(df_CASCADE['real_utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis + W, df_RAELLA['utilization'], 1.8 * W, label='RAELLA', color='#FF8624', edgecolor='black')
plt.text(len(x) - 1 + W, 1.05 * df_RAELLA['utilization'][len(x) - 1], round(df_RAELLA['utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis + 3 * W, df_ResPIM['utilization'], 1.8 * W, label='MINA', color='#53C43C', edgecolor='black')
plt.text(len(x) - 1 + 3 * W, 1.01 * df_ResPIM['utilization'][len(x) - 1], round(df_ResPIM['utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.xticks(x_axis, x)
plt.yticks(np.arange(0, 110, 10))
plt.text(-0.7, 109, '(a)', fontsize=14)
plt.ylabel('Utilization (%)', weight='bold')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.13), ncol=4)
plt.savefig('util.pdf', bbox_inches='tight')
plt.show()
