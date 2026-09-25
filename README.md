# The Book of Common Worship (1906)

A corrected, structured transcription of *The Book of Common Worship*, published by authority of the General Assembly of the Presbyterian Church in the United States of America (Philadelphia: Presbyterian Board of Publication and Sabbath-School Work, 1906), with a lightly modernized edition alongside.

This repository is the working space for editing the text and publishing it, first as a website (GitHub Pages) and later, possibly, as a printed book (Amazon KDP).

**Website:** <https://schrjacob.github.io/book-of-common-worship-1906/>

## Layout

| Path | Contents |
| --- | --- |
| `manuscript/book-of-common-worship-1906.md` | The original 1906 text in Markdown. |
| `manuscript/book-of-common-worship-1906-light.md` | The lightly modernized text, block for block parallel to the original. |
| `docs/` | The website (served by GitHub Pages). `docs/data/book.js` is generated; don't edit it. |
| `scripts/build_site.py` | Rebuilds `docs/data/book.js` from the two manuscripts. |
| `scripts/modernize/` | How the light edition was produced: the first mechanical pass, the block-by-block hand revisions, the list of texts kept unchanged, and a QA check. |
| `review/ocr-corrections.csv` | Every change made to the raw OCR, one row per change, for review. |
| `tools/apply_review.py` | Applies accept / reject / edit decisions from the CSV back to the original manuscript. |
| `source/internet-archive/` | The Internet Archive EPUB (`bookofcommonwor00pres`), as downloaded and extracted. |
| `reference/` | Earlier typesetting work (`A Treasury of Prayers.pdf`). |

## The website

A single page that opens straight into the book, with:

- **Three views:** *Original*, *Side by side* and *Modernized*. The choice is remembered, and can be linked with `?view=original|parallel|modern`.
- **Contents panel:** on the left, shown by default and hidden with the **Contents** button. It lists the major parts (`##`), and each expands accordion-style to its sections (`###`) and prayers (`####`). Opening one branch closes the others, and the panel follows along as you scroll. On phones it is a slide-in drawer.
- **Other features:** light and dark themes, and deep links to any heading (`#the-invocation`, `#family-prayers`, …).

It is plain HTML, CSS and JavaScript with no dependencies apart from Google Fonts. The design follows the *puritan-parallels* site.

### Editing and rebuilding

Edit either manuscript, then run:

```bash
python scripts/build_site.py
```

Commit the regenerated `docs/data/book.js` with your edit.

The two manuscripts must stay **block for block parallel**: the same headings at the same levels, and the same number of paragraphs in the same order. A block is anything separated by a blank line. If they drift out of step, the build stops and names the first block that differs, rather than pairing the wrong texts.

To preview locally:

```bash
cd docs && python -m http.server 8000
```

Then open <http://localhost:8000>.

## The light modernization

The light edition keeps the sentence structure and liturgical register of 1906, and changes only what a modern reader would stumble over:

- **Address to God:** *Thee/Thou/Thy/Thine* → *You/Your/Yours*, keeping the book's reverential capital. Verb forms change to match (*Thou hast* → *You have*, *hath* → *has*, *cometh* → *comes*).
- **Archaic words and constructions:** *beseech* → *pray/ask*, *vouchsafe* → *grant/be pleased*, *unto* → *to*, *nigh* → *near*, *succour* → *help*, *Holy Ghost* → *Holy Spirit*, *forasmuch as* → *since*.
- **Rubrics:** modern word order (*Then shall the Minister say* → *Then the Minister shall say*) and present-tense conditions (*if it be* → *if it is*).
- **Spelling:** American (*honour* → *honor*, *Saviour* → *Savior*, *fulness* → *fullness*).

**Left exactly as printed**, in the words of the King James Version:

- all Holy Scripture, including the Psalter, the lessons, the Sentences, the Commandments and Beatitudes, and Scripture quoted within prayers and exhortations (e.g. *Suffer the little children to come unto me*; *enter thou into the joy of thy Lord*);
- the Lord's Prayer, the Apostles' Creed and the Gloria Patri;
- the ancient hymns and canticles;
- the marriage vows and ring formula, the metrical hymns, the Sursum Corda and Sanctus, and the Scripture benedictions and ascriptions.

Where a prayer adapts a Scripture phrase into its own address to God (e.g. *Praise waiteth for Thee, O God, in Zion* → *Praise waits for You in Zion*), the adaptation is part of the prayer and is modernized. The list of unchanged texts is in `scripts/modernize/fixed.py`, and `scripts/modernize/check.py` confirms that every one of them is identical to the original.

The modernization is editorial work for this site, and the text is meant to be reviewed and refined. From here on, edit `book-of-common-worship-1906-light.md` directly. The scripts in `scripts/modernize/` are a record of how it was produced; re-running them would overwrite hand edits.

## Source

The text was built from the Internet Archive scan [bookofcommonwor00pres](https://archive.org/details/bookofcommonwor00pres) (Princeton Theological Seminary Library copy). Its OCR was cleaned up and every page proofread. About 150 pages were checked against the page images, and the Psalter was compared word by word with the King James Version. Printed page *N* corresponds to scan page *N* + 16; the scan page numbers are the ones used in the CSV.

## Conventions in the manuscripts

- `#` book title · `##` each Order or major part · `###` sections and Psalter Selections · `####` individual prayers and Psalms.
- Rubrics are set as `¶ *italic text*`. Speaker labels (*Minister.*, *Answer.*, *People.*) are italic.
- The opening word of each prayer is in capitals, where the print has a drop capital and small capitals ("ALMIGHTY God…").
- Hymns, the Grace, the marriage vows and the versicles and responses keep their printed line breaks (a `\` at line end).
- The 1906 edition's own spellings are kept in the original, e.g. *show*, *defense*, *loving-kindness*, and both *forever* and *for ever* as printed.
- **Psalter numbering differs between the editions.** The original keeps the 1906 print's verse numbers, which run continuously through each Selection for responsive reading, along with its printing slips. The light edition numbers each verse by its KJV Psalm verse (Psalm 8 starts again at 1) and corrects those slips: it supplies the missing "Psalm 28: 6-9" heading in Selection 8, puts the right headings on Psalms 29 and 30 in Selection 9, gives Psalm 107 its true range (23-43), and joins Psalm 40:5, which the print splits into two numbered lines. The wording of every verse is the same in both.
- `{blank}` (or `#### {blank}` for a heading) holds a place in one manuscript where the other has an extra block, so the two stay aligned. It renders as nothing. There are two: the supplied Psalm 28 heading, and the second half of Psalm 40:5.
- The Creed's footnote and the Ordination margin note are Markdown footnotes (`[^creed1]`, `[^p93]`).
- Printed page numbers, running heads and line-end hyphenation have been removed.
- Five places in the original manuscript needing an editorial decision are marked with invisible `<!--REVIEW: …-->` comments. Search for `REVIEW` to find them.

## Reviewing the OCR corrections

Open `review/ocr-corrections.csv` in a spreadsheet. Filter by **Category** or **Flag**, then enter `reject` or `edit` in the decision column, with your wording in the last column for edits. Then run:

```bash
python tools/apply_review.py manuscript/book-of-common-worship-1906.md review/ocr-corrections.csv
```

A `.bak` backup of the manuscript is written first. Some rows can't be applied automatically: removed rubric marks, rewritten pages, and edits that cross formatting. The script lists those so you can edit the manuscript by hand.

## Status

- [x] Complete text transcribed and proofread
- [x] Lightly modernized edition
- [x] Website
- [ ] Review OCR corrections, the five `REVIEW` items, and the modernization
- [ ] Print edition (KDP)

## Copyright

The 1906 text is in the public domain in the United States. The modernized text is original editorial work for this project.
