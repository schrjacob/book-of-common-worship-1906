"""
Apply your decisions from the corrections CSV back to the Markdown text.

Usage (from the repository root):
    python tools/apply_review.py manuscript/book-of-common-worship-1906.md review/ocr-corrections.csv

For each row:
  * "Your decision" = reject  -> the Correction is replaced by the Original OCR text
  * "Your decision" = edit    -> the Correction is replaced by "Your text (if edit)"
  * anything else (blank / accept) -> no change
The row's Context column (5 words either side, correction in [ ]) is used to find the exact spot.
Markdown markup (*, ¶, #, line-break backslashes) between words is tolerated when matching.
Rows that cannot be located unambiguously are reported and skipped; nothing else is touched.
A backup of the Markdown file is written next to it (.bak) before any change.
"""
import csv, re, shutil, sys

md_path, csv_path = sys.argv[1], sys.argv[2]
text = open(md_path, encoding='utf-8').read()
GAP = r'(?:[\s*¶#>|\\]|<!--.*?-->)+'   # whitespace or markup between words

def words_pattern(words, strict=False):
    if strict:
        return GAP.join(re.escape(w) for w in words)
    # context words: tolerate heading punctuation that was dropped in the final text
    return GAP.join(re.escape(w.rstrip('.,;:')) + r'[.,;:]?' for w in words)

changed = skipped = 0
with open(csv_path, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f):
        decision = (row.get('Your decision (accept / reject / edit)') or '').strip().lower()
        if decision not in ('reject', 'edit'):
            continue
        new = row['Original OCR'] if decision == 'reject' else (row.get('Your text (if edit)') or '')
        m = re.match(r'^(.*?)\[(.*)\](.*)$', row['Context (correction in [ ])'] or '')
        if not m or not row['Correction']:
            print(f"ID {row['ID']}: nothing to locate (deletion or page rewrite) - please edit the Markdown by hand"); skipped += 1; continue
        before, corr, after = m.group(1).split(), m.group(2).split(), m.group(3).split()
        pat = (words_pattern(before) + GAP if before else '') + '(' + words_pattern(corr, strict=True) + ')' + (GAP + words_pattern(after) if after else '')
        hits = list(re.finditer(pat, text, re.S))
        occ = (row.get('Occurrence of context') or '').strip()
        if len(hits) == 1:
            hit = hits[0]
        elif occ.isdigit() and 1 <= int(occ) <= len(hits):
            hit = hits[int(occ) - 1]
        else:
            print(f"ID {row['ID']}: found {len(hits)} matches for the context; skipped"); skipped += 1; continue
        s, e = hit.span(1)
        if new == text[s:e]:
            continue                                   # nothing to do
        if re.search(r'[*¶#|\\]|<!--|\n', text[s:e]):
            print(f"ID {row['ID']}: the text to replace spans formatting; please edit by hand"); skipped += 1; continue
        text = text[:s] + new + text[e:]
        changed += 1

if changed:
    shutil.copyfile(md_path, md_path + '.bak')
    open(md_path, 'w', encoding='utf-8').write(text)
print(f'{changed} change(s) applied, {skipped} skipped.')
