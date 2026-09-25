"""
Build the website data file from the two manuscripts.

    python scripts/build_site.py

Reads
    manuscript/book-of-common-worship-1906.md         (original text)
    manuscript/book-of-common-worship-1906-light.md   (lightly modernized text)
and writes
    docs/data/book.js                                  (GENERATED - do not edit)

The two manuscripts must have the same block structure: the same headings at the
same levels, and the same number of paragraphs, lists, tables and notes, in the
same order. Where one manuscript has a block the other lacks, put `{blank}`
(or `#### {blank}` for a heading) in the other to hold its place. Each original block is paired with the light block in the same
position. If the files drift out of step the build stops and names the first
place where they differ, rather than silently mis-pairing the text.

Only the Python standard library is used.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / 'manuscript' / 'book-of-common-worship-1906.md'
LIGHT = ROOT / 'manuscript' / 'book-of-common-worship-1906-light.md'
OUT = ROOT / 'docs' / 'data' / 'book.js'

BS = '\\'


# ---------------------------------------------------------------- parsing

def split_blocks(text):
    """Split Markdown into blocks separated by blank lines; drop HTML comments."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = text.replace('\r\n', '\n')
    blocks = []
    for raw in re.split(r'\n\s*\n', text):
        raw = raw.strip('\n')
        if raw.strip():
            blocks.append(raw.strip())
    return blocks


def classify(block):
    """Return (kind, info) for a block."""
    m = re.match(r'^(#{1,6})\s+(.*)$', block)
    if m and '\n' not in block:
        return 'h', len(m.group(1))
    if re.match(r'^\[\^([\w-]+)\]:', block):
        return 'fn', None
    if block.startswith('|'):
        return 'table', None
    if all(l.startswith('>') for l in block.split('\n')):
        return 'quote', None
    if all(re.match(r'^\s*- ', l) for l in block.split('\n')):
        return 'list', None
    if block == '---':
        return 'hr', None
    return 'p', None


def inline(md):
    """Convert the small subset of inline Markdown used in the manuscript to HTML."""
    s = html.escape(md, quote=False)
    s = s.replace(' ' + BS + '\n', '<br>').replace(BS + '\n', '<br>')
    s = re.sub(r'\[\^([\w-]+)\]', r'<sup class="fnref"><a href="#fn-\1" id="fnref-\1">*</a></sup>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s, flags=re.S)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s, flags=re.S)
    s = s.replace('\n', ' ')
    return s


def is_blank(block):
    """`{blank}` (or `#### {blank}`) holds a place in one manuscript where the other has a block
    with no counterpart, so the two stay aligned. It renders as nothing."""
    return re.sub(r'^#{1,6}\s+', '', block).strip() == '{blank}'


def render(block, kind):
    """Render one block (original or light) to HTML, plus a CSS class."""
    if is_blank(block):
        return '', ''
    if kind == 'h':
        text = re.sub(r'^#{1,6}\s+', '', block)
        return inline(text), ''
    if kind == 'fn':
        m = re.match(r'^\[\^([\w-]+)\]:\s*(.*)$', block, flags=re.S)
        return f'<span class="fnmark" id="fn-{m.group(1)}">*</span> ' + inline(m.group(2)), 'footnote'
    if kind == 'table':
        rows = [r for r in block.split('\n') if not re.match(r'^\|\s*-', r)]
        out = []
        for i, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip('|').split('|')]
            tag = 'th' if i == 0 else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
        return '<table>' + ''.join(out) + '</table>', 'table'
    if kind == 'quote':
        inner = '\n'.join(re.sub(r'^>\s?', '', l) for l in block.split('\n'))
        paras = [p for p in re.split(r'\n\s*\n', inner) if p.strip()]
        return ''.join(f'<p>{inline(p.strip())}</p>' for p in paras), 'boxed'
    if kind == 'list':
        items = []
        for l in block.split('\n'):
            depth = (len(l) - len(l.lstrip(' '))) // 2
            items.append((depth, inline(re.sub(r'^\s*- ', '', l))))
        out, open_depth = [], -1
        for depth, text in items:
            while open_depth < depth:
                out.append('<ul>'); open_depth += 1
            while open_depth > depth:
                out.append('</ul>'); open_depth -= 1
            out.append(f'<li>{text}</li>')
        out.extend('</ul>' * (open_depth + 1))
        return ''.join(out), 'list'
    if kind == 'hr':
        return '', 'rule'
    cls = []
    if block.startswith('¶'):
        cls.append('rubric')
    if (' ' + BS + '\n') in block or block.endswith(BS):
        cls.append('verse')
    if re.match(r'^\d+ ', block):
        cls.append('psalm-verse')
    return inline(block), ' '.join(cls)


def slugify(text, used):
    base = re.sub(r'<[^>]+>', '', text)
    base = html.unescape(base).lower()
    base = re.sub(r"['’]", '', base)
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-') or 'section'
    base = base[:60].rstrip('-')
    slug, n = base, 2
    while slug in used:
        slug = f'{base}-{n}'; n += 1
    used.add(slug)
    return slug


# ---------------------------------------------------------------- build

def build():
    orig = split_blocks(ORIGINAL.read_text(encoding='utf-8'))
    light = split_blocks(LIGHT.read_text(encoding='utf-8'))

    problems = []
    if len(orig) != len(light):
        problems.append(f'original has {len(orig)} blocks, light has {len(light)}')
    for i, (o, l) in enumerate(zip(orig, light)):
        ko, lo = classify(o)
        kl, ll = classify(l)
        if (ko, lo) != (kl, ll):
            problems.append(f'block {i + 1}: original is {ko}{lo or ""}, light is {kl}{ll or ""}\n'
                            f'    original: {o[:100]!r}\n    light:    {l[:100]!r}')
            break
    if problems:
        print('Build stopped - the manuscripts are out of step:')
        for p in problems:
            print('  ' + p)
        sys.exit(1)

    used = set()
    blocks = []
    chain = {}                                   # current heading id at each level
    identical = 0
    for o, l in zip(orig, light):
        kind, level = classify(o)
        oh, cls = render(o, kind)
        lh, lcls = render(l, kind)
        cls = cls or lcls
        rec = {'k': kind, 'o': oh}
        if is_blank(o):
            rec['ob'] = 1                        # nothing in the original here
        if is_blank(l):
            rec['lb'] = 1                        # nothing in the light edition here
        if lh != oh:
            rec['l'] = lh                        # omitted when identical, to keep the file small
        else:
            identical += 1
        if cls:
            rec['c'] = cls
        if kind == 'h':
            rec['lv'] = level
            rec['id'] = slugify(oh or lh, used)
            chain[level] = rec['id']
            for deeper in [k for k in chain if k > level]:
                del chain[deeper]
        blocks.append(rec)

    title = next((re.sub(r'<[^>]+>', '', b['o']) for b in blocks if b['k'] == 'h' and b['lv'] == 1), 'Book')
    data = {'title': title, 'blocks': blocks}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('/* GENERATED by scripts/build_site.py - do not edit. */\nwindow.BOOK = '
                   + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    heads = sum(1 for b in blocks if b['k'] == 'h')
    print(f'Wrote {OUT.relative_to(ROOT)}: {len(blocks)} blocks ({heads} headings), '
          f'{len(blocks) - identical} differ between original and light, {OUT.stat().st_size // 1024} KB')


if __name__ == '__main__':
    build()
