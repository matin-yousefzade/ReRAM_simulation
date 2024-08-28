import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

W = 0.22
rcParams['font.weight'] = 'bold'

df_ISAAC = pd.read_csv('../results/ISAAC_TT.csv')

x = list(df_ISAAC['dnn'])[0 : 7]
x_axis = np.arange(len(x))

plt.figure(figsize=(8, 4))
ax = plt.axes()
ax.set_axisbelow(True)
plt.grid(axis='y')

plt.bar(x_axis, list(df_ISAAC['minimum_required_chips'])[0 : 7], 1.8 * W, label='ISAAC', color='#0060FF', edgecolor='black')

plt.xticks(x_axis, x)
plt.yticks(np.arange(0, 11, 1))
plt.ylabel('Minimum Required Chips', weight='bold')
plt.savefig('ws_min_req_chips.pdf', bbox_inches='tight')
plt.show()
