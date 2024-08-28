import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

def plot_util(mode):
    W = 0.17
    ALPHA = 40
    rcParams['font.weight'] = 'bold'

    df_ISAAC = pd.read_csv('../results2/ISAAC_' + mode + '.csv')
    df_RAELLA = pd.read_csv('../results2/RAELLA_' + mode + '.csv')

    x = list(df_ISAAC['dnn'])
    x_axis = np.arange(len(x))

    plt.figure(figsize=(8,4))
    ax = plt.axes()
    ax.set_axisbelow(True)
    plt.grid(axis='y')

    plt.bar(x_axis - W, df_ISAAC['utilization'], 1.8 * W, label='ISAAC', color='#0060FF', edgecolor='black')
    plt.text(len(x) - 1 - W, 1.05 * df_ISAAC['utilization'][len(x) - 1], round(df_ISAAC['utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

    plt.bar(x_axis + W, df_RAELLA['utilization'], 1.8 * W, label='RAELLA', color='#FF8624', edgecolor='black')
    plt.text(len(x) - 1 + W, 1.05 * df_RAELLA['utilization'][len(x) - 1], round(df_RAELLA['utilization'][len(x) - 1], 1), ha='center', rotation=ALPHA)

    plt.xticks(x_axis, x)
    plt.ylabel('Utilization (%)', weight='bold')
    if (mode == 'FF'):
        plt.yticks(np.arange(0, 5.5, 0.5))
        plt.text(len(x) - 1 + W + 0.05, 4.65, '(a)', fontsize=14)
    if (mode == 'TF'):
        plt.yticks(np.arange(0, 22, 2))
        plt.text(len(x) - 1 + W + 0.05, 18.5, '(b)', fontsize=14)
    if (mode == 'FT'):
        plt.yticks(np.arange(0, 22, 2))
        plt.text(len(x) - 1 + W + 0.05, 18.5, '(c)', fontsize=14)
    if (mode == 'TT'):
        plt.yticks(np.arange(0, 33, 3))
        plt.text(len(x) - 1 + W + 0.05, 27.8, '(d)', fontsize=14)
    plt.legend(loc='upper left')
    plt.savefig('ws_util_' + mode + '.pdf', bbox_inches='tight')
    plt.show()

plot_util('FF')
plot_util('TF')
plot_util('FT')
plot_util('TT')
