# Dictionary source evaluation — Phase 3.1

Reviewed 2026-10-20. Links below are primary project documentation, inspected during
implementation. Coverage means documented fields, not independently reviewed linguistic
accuracy. No website search pages are scraped and no machine translations are generated.

Phase 3.1.1 adds separate Vietnamese character notes, described below; it does not add
Vietnamese lexical definitions to the original CC-CEDICT selection.

| Candidate | Verified coverage | Missing or unverified coverage | Acquisition, size, updates, search | Licensing / decision |
| --- | --- | --- | --- | --- |
| [CC-CEDICT official download](https://www.mdbg.net/chinese/dictionary?page=cedict) | Simplified and traditional headwords, numbered-tone Mandarin pinyin, multiple English glosses, compounds | No structured Vietnamese definitions, lexical Sino-Vietnamese, POS, reviewed examples/translations or audio in the selected format | Downloadable UTF-8 v1 archive; page reported 125,303 entries, release 2026-10-19 20:24:47 GMT. Community corrections released frequently, no promised cadence. Local indexed search implemented here | Selected. Official page currently specifies CC BY-SA 4.0; commercial use permitted subject to conditions. No per-query cost/rate limit for local data. Download manually through the offered dataset link; automated website access is prohibited |
| [CVDICT](https://raw.githubusercontent.com/ph0ngp/CVDICT/master/README.md) | README describes 122,000+ CC-CEDICT-derived words/phrases with original Chinese forms/pinyin and Vietnamese translations | README explicitly identifies fine-tuned ChatGPT-4o translation and remaining errors; lexical reading, examples, POS/audio coverage not established | Download/release offered; update cadence and reliable field-level review status unverified; no documented hosted query API examined | README claims CC BY-SA 4.0. Rejected for this slice: AI-generated Vietnamese translations lack the required review provenance. Free/nonprofit project description is not itself a commercial restriction in that license |
| [Kaikki Chinese / Wiktionary extraction](https://kaikki.org/dictionary/Chinese/) | Structured senses and POS categories; compounds; the displayed extraction derives from English Wiktionary | Mandarin-specific pronunciation/form association, Vietnamese meaning coverage, lexical Sino-Vietnamese, example translations and media rights need field-level auditing; not guaranteed across entries | Inspected page: 307,224 distinct forms, 1.1 GB postprocessed download, September 2026 dump / October extraction. Postprocessed format deprecated; raw extraction preferred. Local processing possible; no hosted production lookup SLA verified | [Wikimedia terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) govern text reuse; attribution/share-alike and imported-content notices require preservation. Media can have separate licenses. Deferred: much larger, heterogeneous parsing and provenance work |
| [Unicode Unihan](https://www.unicode.org/reports/tr38/) | Character properties include Mandarin, variants and provisional kVietnamese readings | Character readings are not Vietnamese definitions or context-verified compound readings; no complete lexical senses/POS/examples/audio | Versioned UTF-8 files; character lookup, not a compound dictionary API. Offline enrichment feasible; version-dependent coverage, not counted as dictionary words | [Unicode license](https://www.unicode.org/license.txt) requires preservation of notices. Deferred enrichment; insufficient as primary lexical source |
| [MediaWiki Action API](https://www.mediawiki.org/wiki/API:Etiquette) over Wiktionary | Publicly documented page retrieval/search API | Page text is not a uniform Chinese–Vietnamese lexical contract; no verified complete pronunciation, Vietnamese or audio coverage | Etiquette requires identifiable clients and respecting throttling/maxlag; no fixed universal quota, price or SLA verified. Local dumps are an alternative | Same content licensing audit as Wiktionary; rejected as runtime dependency because it adds availability/latency and parsing complexity without resolving coverage |

## Decision and obligations

Use a local PostgreSQL CC-CEDICT v1 dictionary, separate from curriculum tables.
Follow the [v1 syntax](https://cc-cedict.org/wiki/format:syntax); accept only that
format rather than silently misreading v2. Preserve source case in pinyin to distinguish
proper names. Source gloss boundaries remain ordered glosses, not inferred ontology/POS.

The [CC BY-SA 4.0 terms](https://creativecommons.org/licenses/by-sa/4.0/) require
appropriate credit, source/license links, notice of modifications and share-alike for
distributed adaptations, with no additional restrictions. Retain upstream copyright,
license and disclaimer notices alongside downloaded/redistributed datasets. API details
carry attribution and transformation notices. Future UI must display those notices;
authentication does not authorize adding restrictions on reuse of the licensed data.
The dataset license must not be confused with a blanket license determination for app code.
Older mirrors may mention 3.0: verify the actual downloaded artifact's notice, and do
not relabel an older artifact as 4.0. The importer requires explicit license acknowledgement.

No production dataset is committed. Acquisition is a manual, license-aware step; import
requires a local file, explicit revision and SHA-256. Full-dataset availability/benchmark
results are recorded separately in dictionary-foundation.md; documentation-page counts
are not claims that that data is installed. A small synthetic fixture tests the format.

Remaining gaps are intentional: English-only meanings; null Vietnamese summary and
Sino-Vietnamese reading; empty structured POS, reviewed examples and audio. No LLM
translation or concatenated character readings fill those gaps. CC-CEDICT community
content is a lookup aid, not reviewed curriculum or evidence of learning completion.

## Phase 3.1.1 Vietnamese enrichment

Rechecked 2026-10-21. A genuine downloadable artifact, source license/notice and pinned
commit were acquired for the selected source; detailed hashes/commands are in
[Vietnamese enrichment](dictionary-vietnamese-enrichment.md).

| Candidate | Verified data and provenance | License/commercial/derivative conditions | Decision and limits |
| --- | --- | --- | --- |
| [hsk-sino-viet](https://github.com/xkhanhs/hsk-sino-viet/tree/7cd2805fb0bb46f8e21bda364b857759465f1ce2) | Downloaded JSON: 659 distinct character records, 116 explicit variants. Publisher notice claims original authored readings/glosses; the private authoring process cannot be independently inspected | LICENSE is CC BY 4.0; commercial adaptation/redistribution permitted with attribution, license and change notices, no extra restrictions; no share-alike requirement | Selected solely for character annotations, flagged as not independently reviewed. No complete compound definitions or lexical sense/pronunciation inventory; HSK/radical/mnemonic/stroke fields excluded |
| [Unihan](https://www.unicode.org/reports/tr38/) | Official character properties include provisional Vietnamese readings, Mandarin and variants. No complete compound dictionary or Vietnamese lexical meanings verified | [Unicode license](https://www.unicode.org/license.txt) permits reuse with its notices; commercial use is not excluded | Reputable future cross-check/enrichment source; not selected for the initial Vietnamese gloss layer. Character readings cannot establish a compound reading |
| [CVDICT README](https://raw.githubusercontent.com/ph0ngp/CVDICT/master/README.md) | Download offered, CC-CEDICT-derived Vietnamese definitions described as largely model translated with remaining errors; no per-sense independent review evidence established | README links CC BY-SA 4.0; preserve derivative attribution/share-alike obligations. It does not supply a blanket guarantee of translation accuracy | Not accepted as reliable lexical Vietnamese enrichment for this task |
| [Wiktionary/Kaikki](https://kaikki.org/dictionary/Chinese/) | Structured lexical extraction is available, but Chinese-to-Vietnamese sense coverage, alignment and individual source/media notices were not established for this slice | Wikimedia content licensing and imported-content notices require field-level review; extractor code licensing does not license every data/media item | Deferred rather than guessing lexical joins or claiming Vietnamese coverage |

No paid API, unknown dump, website scrape or LLM-generated facts are used. Character data
stays separate from CC-CEDICT English senses. Verified findings here concern the artifact,
schema and published permission; they are not an independent certification of every gloss.
