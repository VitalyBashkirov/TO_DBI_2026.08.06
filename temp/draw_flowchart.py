"""
Render horizontal flowchart as PNG using matplotlib.
No network or external binaries required.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

# Find a font that supports Cyrillic
font_family = None
for f in fm.fontManager.ttflist:
    if any(k in f.name.lower() for k in ['dejavu sans', 'arial', 'segoe ui', 'tahoma', 'verdana']):
        font_family = f.name
        break
if not font_family:
    font_family = 'DejaVu Sans'

plt.rcParams['font.family'] = font_family

fig, ax = plt.subplots(figsize=(28, 6))
ax.set_xlim(-0.5, 17.5)
ax.set_ylim(-1.5, 3.5)
ax.axis('off')
ax.set_facecolor('#F5F0E8')

PISTACHIO = '#B7C68B'
GREEN = '#4CAF50'
NODE_COLOR = '#E8F5E0'
BORDER = '#5a8a3a'
LINE = '#3d6b1f'

def draw_box(ax, x, y, text, w=2.0, h=0.8, color=NODE_COLOR, shape='round'):
    if shape == 'round':
        box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                             boxstyle="round,pad=0.12",
                             facecolor=color, edgecolor=BORDER, linewidth=1.5)
    elif shape == 'diamond':
        # Diamond as polygon
        from matplotlib.patches import Polygon
        pts = [(x, y + h/2), (x + w/2, y), (x, y - h/2), (x - w/2, y)]
        box = Polygon(pts, closed=True, facecolor=PISTACHIO, edgecolor=BORDER, linewidth=1.5)
    elif shape == 'stadium':
        box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                             boxstyle="round,pad=0.25",
                             facecolor=GREEN, edgecolor='#2E7D32', linewidth=2.5)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.5, color='black' if shape != 'stadium' else 'white',
            fontweight='bold' if shape == 'stadium' else 'normal', wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, label='', curve=0):
    style = f"arc3,rad={curve}" if curve else "arc3,rad=0"
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle='->', mutation_scale=15,
                            color=LINE, linewidth=1.3,
                            connectionstyle=style)
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 0.15
        ax.text(mx, my, label, ha='center', va='center', fontsize=8,
                color=LINE, fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.8))

# Y positions
Y_MAIN = 1.5
Y_UP = 2.8
Y_DOWN = 0.0

# Nodes (x, y, text, shape)
nodes = {
    'Start': (0, Y_MAIN, 'Старт', 'stadium'),
    'P1':    (2, Y_MAIN, '1. PATCH_IN\n>> PATCH_OUT', 'round'),
    'P3':    (4, Y_MAIN, 'Каталоги\nуказаны?', 'diamond'),
    'P2':    (6, Y_MAIN, 'Настройки:\n*.plp, логи,\npreserve_structure', 'round'),
    'R1':    (8, Y_MAIN, '2. Рубрикатор\nFILES+PROMPTS\nTreeview', 'round'),
    'R3':    (10, Y_MAIN, 'Правило\nвыбрано?', 'diamond'),
    'S1':    (12, Y_MAIN, '3. F5: Сканирование\n*.plp >> scan_report', 'round'),
    'F1':    (14, Y_MAIN, 'preserve\n_structure?', 'diamond'),
    'F3':    (16, Y_MAIN, 'Проблемы\nнайдены?', 'diamond'),
    'F2':    (14, Y_UP, 'Копирование\nструктуры', 'round'),
    'End':   (17, Y_MAIN, 'Конец', 'stadium'),
    'F4':    (16, Y_DOWN, '4. F6: fixer\n>> fix_log', 'round'),
    'F5':    (14, Y_DOWN, 'Авто\nархив?', 'diamond'),
    'F6':    (12, Y_DOWN, '_run_archive', 'round'),
    'A1':    (12, Y_DOWN - 1.2, '5. ZIP+.pck\n>> PATCH_OUT', 'round'),
}

# Draw all nodes
for key, (x, y, text, shape) in nodes.items():
    w = 2.2 if 'diamond' not in shape else 1.8
    h = 0.9
    draw_box(ax, x, y, text, w, h, shape=shape)

# Draw arrows
arrows = [
    ('Start', 'P1', ''),
    ('P1', 'P3', ''),
    ('P3', 'P1', 'Нет', -0.3),  # loop back
    ('P3', 'P2', 'Да'),
    ('P2', 'R1', ''),
    ('R1', 'R3', ''),
    ('R3', 'R1', 'Нет', -0.3),  # loop back
    ('R3', 'S1', 'Да'),
    ('S1', 'F1', ''),
    ('F1', 'F2', 'Да'),
    ('F1', 'F3', 'Нет'),
    ('F2', 'F3', ''),
    ('F3', 'End', 'Нет'),
    ('F3', 'F4', 'Да'),
    ('F4', 'F5', ''),
    ('F5', 'F6', 'Да'),
    ('F5', 'A1', 'Нет'),
    ('F6', 'A1', ''),
    ('A1', 'End', ''),
]

for src, dst, label, *curve in arrows:
    x1, y1 = nodes[src][0], nodes[src][1]
    x2, y2 = nodes[dst][0], nodes[dst][1]
    c = curve[0] if curve else 0
    # Adjust start/end to box edges
    if x2 > x1:
        x1 += 1.1
        x2 -= 1.1
    elif x2 < x1:
        x1 -= 1.1
        x2 += 1.1
    elif y2 > y1:
        y1 += 0.45
        y2 -= 0.45
    elif y2 < y1:
        y1 -= 0.45
        y2 += 0.45
    draw_arrow(ax, x1, y1, x2, y2, label, c)

plt.tight_layout()
plt.savefig('ALGORITHM_FLOWCHART_LR.png', dpi=150, bbox_inches='tight',
            facecolor='#F5F0E8', edgecolor='none')
print("OK saved ALGORITHM_FLOWCHART_LR.png")
