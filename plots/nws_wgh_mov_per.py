import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

W = 0.22
H = 1.5
rcParams['font.weight'] = 'bold'

df_CASCADE = pd.read_csv('../results/CASCADE.csv')

x = list(df_CASCADE['dnn'])
x_axis = np.arange(len(x))

plt.figure(figsize=(8, 4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x_axis, df_CASCADE['memory_access_percentage'], 1.8 * W, label='CASCADE', color='#BA1B01', edgecolor='black')
plt.text(len(x) - 1, df_CASCADE['memory_access_percentage'][len(x) - 1] + H, round(df_CASCADE['memory_access_percentage'][len(x) - 1], 1), ha='center')

plt.xticks(x_axis, x)
plt.yticks(np.arange(0, 110, 10))
plt.ylabel('Weight Movement Percentage (%)', weight='bold')
plt.savefig('nws_wgh_mov_per.pdf', bbox_inches='tight')
plt.show()
