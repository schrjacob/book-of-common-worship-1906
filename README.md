# The Book of Common Worship (1906)

A corrected, structured transcription of *The Book of Common Worship*, published by authority of the General Assembly of the Presbyterian Church in the United States of America (Philadelphia: Presbyterian Board of Publication and Sabbath-School Work, 1906).

This repository is the working space for editing the text and preparing it for publication, first as a GitHub Pages website and later, possibly, as a printed book (Amazon KDP).

## Layout

| Path | Contents |
| --- | --- |
| `manuscript/book-of-common-worship-1906.md` | The full text of the book in Markdown. **This is the file to edit.** |
| `review/ocr-corrections.csv` | Every change made to the raw OCR, one row per change, for review. |
| `tools/apply_review.py` | Applies accept / reject / edit decisions from the CSV back to the manuscript. |
| `source/internet-archive/` | The Internet Archive EPUB (`bookofcommonwor00pres`), as downloaded and extracted. |
| `reference/` | Earlier typesetting work (`A Treasury of Prayers.pdf`). |

## Source

The text was built from the Internet Archive scan [bookofcommonwor00pres](https://archive.org/details/bookofcommonwor00pres) (Princeton Theological Seminary Library copy). Its OCR was cleaned up and every page proofread. About 150 pages were checked against the page images, and the Psalter was compared word by word with the King James Version. Printed page *N* corresponds to scan page *N* + 16; the scan page numbers are the ones used in the CSV.

## Conventions in the manuscript

- `#` book title · `##` each Order or major part · `###` sections and Psalter Selections · `####` individual prayers and Psalms.
- Rubrics are set as `¶ *italic text*`. Speaker labels (*Minister.*, *Answer.*, *People.*) are italic.
- The opening word of each prayer is in capitals, where the print has a drop capital and small capitals ("ALMIGHTY God…").
- Hymns, the Grace, the marriage vows and the versicles and responses keep their printed line breaks (a `\` at line end).
- The 1906 edition's own spellings are kept, e.g. *show*, *defense*, *loving-kindness*, and both *forever* and *for ever* as printed.
- The Creed's footnote and the Ordination margin note are Markdown footnotes (`[^creed1]`, `[^p93]`).
- Printed page numbers, running heads and line-end hyphenation have been removed.
- Five places needing an editorial decision are marked with invisible `<!--REVIEW: …-->` comments. Search for `REVIEW` to find them.

## Reviewing the OCR corrections

Open `review/ocr-corrections.csv` in a spreadsheet. Filter by **Category** or **Flag**, then enter `reject` or `edit` in the decision column, with your wording in the last column for edits. Then run:

```bash
python tools/apply_review.py manuscript/book-of-common-worship-1906.md review/ocr-corrections.csv
```

A `.bak` backup of the manuscript is written first. Some rows can't be applied automatically: removed rubric marks, rewritten pages, and edits that cross formatting. The script lists those so you can edit the manuscript by hand.

## Status

- [x] Complete text transcribed and proofread
- [ ] Review OCR corrections and the five `REVIEW` items
- [ ] GitHub Pages website
- [ ] Print edition (KDP)

## Copyright

The 1906 text is in the public domain in the United States.
