"""Review helper: print blocks with their index, section and fixed status.

    python scripts/modernize/dump.py fixed            # fixed blocks outside Psalter/Canticles
    python scripts/modernize/dump.py modern START END # modernized blocks (original, then light) by index range
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fixed import is_fixed

ROOT = Path(__file__).resolve().parents[2]
def blocks(p):
    t = re.sub(r'<!--.*?-->', '', p.read_text(encoding='utf-8'))
    return [b.strip() for b in re.split(r'\n\s*\n', t) if b.strip()]
O = blocks(ROOT / 'manuscript' / 'book-of-common-worship-1906.md')
L = blocks(ROOT / 'manuscript' / 'book-of-common-worship-1906-light.md')
assert len(O) == len(L), (len(O), len(L))
ctx = []; info = []
for i, b in enumerate(O):
    m = re.match(r'^(#{1,6}) (.*)$', b)
    if m and '\n' not in b:
        lv = len(m.group(1)); ctx = (ctx + [''] * lv)[:lv - 1] + [m.group(2)]
        info.append(('h', list(ctx))); continue
    info.append(('fixed' if is_fixed(b, ctx) else 'mod', list(ctx)))

mode = sys.argv[1]
if mode == 'fixed':
    for i, (k, c) in enumerate(info):
        if k == 'fixed' and not any(x in ('The Psalter', 'Ancient Hymns and Canticles', 'Table of Contents') for x in c):
            print(i, '|', c[-1][:30], '|', O[i][:90].replace('\n', ' '))
elif mode == 'light':
    a, b = int(sys.argv[2]), int(sys.argv[3])
    for i in range(a, min(b, len(O))):
        k, c = info[i]
        if k == 'h': print(f'## {O[i]}'); continue
        if k == 'mod': print(f'[{i}] {L[i]}')
else:
    a, b = int(sys.argv[2]), int(sys.argv[3])
    last = None
    for i in range(a, min(b, len(O))):
        k, c = info[i]
        if k == 'h':
            print(f'\n######## {O[i]}'); continue
        if k != 'mod': continue
        print(f'[{i}] O: {O[i]}')
        print(f'[{i}] L: {L[i]}' if L[i] != O[i] else f'[{i}] L: (same)')
