import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.weight'] = 'bold'

df_CASCADE = pd.read_csv('../results/CASCADE.csv')

energy = {
    'ReRAM\nWrite': df_CASCADE.iloc[-1]['MAC_RRAM_write'] + df_CASCADE.iloc[-1]['buffer_RRAM_write'],
    'Weight\nMovement': df_CASCADE.iloc[-1]['DRAM'],
    'DAC': df_CASCADE.iloc[-1]['DAC'],
    'eDRAM': df_CASCADE.iloc[-1]['eDRAM'],
    'ReRAM\nRead': df_CASCADE.iloc[-1]['MAC_RRAM_read'] + df_CASCADE.iloc[-1]['buffer_RRAM_read'],
    'ADC': df_CASCADE.iloc[-1]['ADC'],
    'Others': df_CASCADE.iloc[-1]['IR'] + df_CASCADE.iloc[-1]['OR']
}

plt.figure(figsize=(8, 4))
colors = ['#E3191C', '#FC4E29', '#FD8D3C', '#FEB14C', '#FED976', '#FFFFB3', '#FFFFE0']
wedgeprops = {'edgecolor': 'black', 'linewidth': 0.5, 'antialiased': True}
plt.pie(list(energy.values()), labels=list(energy.keys()), colors=colors, wedgeprops=wedgeprops, autopct='%1.1f%%', pctdistance=0.8)
plt.savefig('nws_energy.pdf', bbox_inches='tight')
plt.show()
