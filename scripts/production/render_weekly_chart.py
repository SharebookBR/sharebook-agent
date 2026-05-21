import matplotlib.pyplot as plt

labels = ['2026-W08','2026-W09','2026-W10','2026-W11','2026-W12','2026-W13','2026-W14','2026-W15','2026-W16','2026-W17','2026-W18','2026-W19','2026-W20','2026-W21']
sessions = [87,289,338,324,119,162,216,264,685,209,247,259,208,109]
signups = [11,15,21,36,12,13,14,7,17,10,10,14,18,3]
conversion = [12.64,5.19,6.21,11.11,10.08,8.02,6.48,2.65,2.48,4.78,4.05,5.41,8.65,2.75]

plt.style.use('dark_background')
fig, ax1 = plt.subplots(figsize=(14, 8), dpi=160)
fig.patch.set_facecolor('#0f172a')
ax1.set_facecolor('#111827')

l1 = ax1.plot(labels, sessions, color='#60a5fa', marker='o', linewidth=2.5, label='Sessões')
l2 = ax1.plot(labels, signups, color='#34d399', marker='o', linewidth=2.5, label='Cadastros')
ax1.set_ylabel('Sessões / Cadastros', color='#cbd5e1')
ax1.tick_params(axis='x', rotation=35, colors='#94a3b8')
ax1.tick_params(axis='y', colors='#94a3b8')
ax1.grid(True, color='#1f2937', alpha=0.8)

ax2 = ax1.twinx()
l3 = ax2.plot(labels, conversion, color='#f59e0b', marker='o', linewidth=2.5, label='Conversão %')
ax2.set_ylabel('Conversão %', color='#f59e0b')
ax2.tick_params(axis='y', colors='#f59e0b')

plt.title('Sharebook, Sessões x Cadastros por semana (últimos 90 dias)', color='white', fontsize=16, pad=20)

lines = l1 + l2 + l3
labels_legend = [l.get_label() for l in lines]
leg = ax1.legend(lines, labels_legend, loc='upper left', frameon=True, facecolor='#0b1220', edgecolor='#1f2937')
for text in leg.get_texts():
    text.set_color('#e5e7eb')

fig.text(0.12, 0.90, 'Sessões totais\n3.516', color='white', fontsize=12, bbox=dict(facecolor='#0b1220', edgecolor='#1f2937', boxstyle='round,pad=0.5'))
fig.text(0.32, 0.90, 'Cadastros totais\n201', color='white', fontsize=12, bbox=dict(facecolor='#0b1220', edgecolor='#1f2937', boxstyle='round,pad=0.5'))
fig.text(0.49, 0.90, 'Conversão média\n5,72%', color='white', fontsize=12, bbox=dict(facecolor='#0b1220', edgecolor='#1f2937', boxstyle='round,pad=0.5'))

plt.tight_layout(rect=[0, 0, 1, 0.88])
out = '/data/workspace/sharebook-agent/var/weekly-sessions-signups.png'
import os
os.makedirs('/data/workspace/sharebook-agent/var', exist_ok=True)
plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches='tight')
print(out)
