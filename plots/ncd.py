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

normalized_cd_ISAAC = np.divide(df_ISAAC['computational_density'], df_ISAAC['computational_density'])
normalized_cd_CASCADE = np.divide(df_CASCADE['computational_density'], df_ISAAC['computational_density'])
normalized_cd_RAELLA = np.divide(df_RAELLA['computational_density'], df_ISAAC['computational_density'])
normalized_cd_ResPIM = np.divide(df_ResPIM['computational_density'], df_ISAAC['computational_density'])

x = list(df_ISAAC['dnn'])
x_axis = np.arange(len(x))

plt.figure(figsize=(8, 4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x_axis - 3 * W, normalized_cd_ISAAC, 1.8 * W, label='ISAAC', color='#0060FF', edgecolor='black')
plt.text(len(x) - 1 - 3 * W, 1.25 * normalized_cd_ISAAC[len(x) - 1], round(normalized_cd_ISAAC[len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis - W, normalized_cd_CASCADE, 1.8 * W, label='CASCADE', color='#BA1B01', edgecolor='black')
plt.text(len(x) - 1 - W, 1.05 * normalized_cd_CASCADE[len(x) - 1], round(normalized_cd_CASCADE[len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis + W, normalized_cd_RAELLA, 1.8 * W, label='RAELLA', color='#FF8624', edgecolor='black')
plt.text(len(x) - 1 + W, 1.15 * normalized_cd_RAELLA[len(x) - 1], round(normalized_cd_RAELLA[len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.bar(x_axis + 3 * W, normalized_cd_ResPIM, 1.8 * W, label='MINA', color='#53C43C', edgecolor='black')
plt.text(len(x) - 1 + 3 * W, 1.02 * normalized_cd_ResPIM[len(x) - 1], round(normalized_cd_ResPIM[len(x) - 1], 1), ha='center', rotation=ALPHA)

plt.xticks(x_axis, x)
plt.yticks(np.arange(0, 22, 2))
plt.text(-0.7, 21, '(b)', fontsize=14)
plt.ylabel('Normalized Computational Density', weight='bold')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.13), ncol=4)
plt.savefig('ncd.pdf', bbox_inches='tight')
plt.show()
