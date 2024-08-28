import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.weight'] = 'bold'

tile_per_chip = 128
ima_per_tile = 9
cu_per_ima = 64

area = {
    'Crossbar': tile_per_chip * ima_per_tile * cu_per_ima * 400,
    'Configuration Array': tile_per_chip * ima_per_tile * cu_per_ima * 360,
    'eDRAM': 16268000,
    'ADC': tile_per_chip * ima_per_tile * 8703.01,
    'Weight Memory': tile_per_chip * ima_per_tile * cu_per_ima * 100,
    'IR': tile_per_chip * ima_per_tile * 360,
    'IMA_OR': tile_per_chip * ima_per_tile * 360,
    'DAC': tile_per_chip * ima_per_tile * 170,
    'Tile_OR': tile_per_chip * 1181.25,
    'SH': tile_per_chip * ima_per_tile * cu_per_ima * 1.211
}

summarized_area = {
    'Crossbar': area['Crossbar'],
    'Config\nArray': area['Configuration Array'],
    'eDRAM': area['eDRAM'],
    'ADC': area['ADC'],
    'Weight\nMemory': area['Weight Memory'],
    'Others': area['IR'] + area['IMA_OR'] + area['DAC'] + area['Tile_OR'] + area['SH']
}

df_ResPIM = pd.read_csv('../results/ResPIM.csv')

energy = {
    'Crossbar': df_ResPIM.iloc[-1]['CB'],
    'ADC': df_ResPIM.iloc[-1]['ADC'],
    'DAC': df_ResPIM.iloc[-1]['DAC'],
    'eDRAM': df_ResPIM.iloc[-1]['eDRAM'],
    'Tile_OR': df_ResPIM.iloc[-1]['tile_OR'],
    'IR': df_ResPIM.iloc[-1]['IR'],
    'IMA_OR': df_ResPIM.iloc[-1]['IMA_OR'],
    'Configuration Array': df_ResPIM.iloc[-1]['configuration_array'],
    'SH': df_ResPIM.iloc[-1]['SH'],
    'Weight Memory': df_ResPIM.iloc[-1]['weight_memory']
}

summarized_energy = {
    'Crossbar': energy['Crossbar'],
    'ADC': energy['ADC'],
    'DAC': energy['DAC'],
    'eDRAM': energy['eDRAM'],
    'Others': energy['Tile_OR'] + energy['IR'] + energy['IMA_OR'] + energy['Configuration Array'] + energy['SH'] + energy['Weight Memory']
}

plt.figure(figsize=(6.93, 3.84))

plt.subplot(1, 2, 1)
colors = ['#005acd', '#0093cb', '#6dd7fd', '#bef0ff', '#deffff', '#f5ffff']
wedgeprops = {'edgecolor': 'black', 'linewidth': 0.5, 'antialiased': True}
plt.pie(list(summarized_area.values()), labels=list(summarized_area.keys()), radius=1.1, colors=colors, wedgeprops=wedgeprops, autopct='%1.1f%%', pctdistance=0.8)
plt.title('Area Breakdown', weight='bold')

plt.subplot(1, 2, 2)
colors = ['#E3191C', '#FC4E29', '#FD8D3C', '#FED976', '#FFFFB3']
wedgeprops = {'edgecolor': 'black', 'linewidth': 0.5, 'antialiased': True}
plt.pie(list(summarized_energy.values()), labels=list(summarized_energy.keys()), radius=1.1, colors=colors, wedgeprops=wedgeprops, autopct='%1.1f%%', pctdistance=0.8)
plt.title('Energy Breakdown', weight='bold')

plt.text(-4.55, 1.7, '(d)', fontsize=14)
plt.savefig('area_energy.pdf')
plt.show()
