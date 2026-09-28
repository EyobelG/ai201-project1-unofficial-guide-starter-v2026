# The Unofficial Guide

Eyobel Gebre — corpus: city_guides

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a small RAG system built on the `city_guides` corpus: fourteen
travel guides for fictional towns, each broken into sections like "Getting
there," "Eat and drink," and "When to go." Ask it something a guide would
actually cover, like travel times, opening months, or walk lengths, and it
retrieves the relevant section and answers from it, naming the file. Ask it
something the corpus doesn't cover and it says so instead of guessing.

## Chunking Strategy

**Chunk size:** 800 characters, used only as a ceiling — most chunks are much shorter than this
**Overlap:** 120 characters, used only when a section has to be force-split

Every guide is the same shape: a `#` title, then six or seven `##` sections
("Getting there", "Eat and drink", "When to go"...) each 150-500 characters.
The old fixed 800-char window kept cutting mid-section — gluing "Getting
there" onto "Getting around," or slicing an answer in half. Each `##` section
is already a complete thought, so I chunk on headers instead: one chunk per
section, heading included. Chunk size/overlap only matter as a fallback for
the rare oversized section, splitting on paragraphs first, then characters.

Went with this from the start — no fixed-size baseline to walk back from.

## Sample Chunks


**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#6` — produced by: `chunker.py::split_documents`

```
## When to go

May to September. Outside those months the pub in the third village closes, the farm shop reduces its hours, and several footpaths become genuinely boggy rather than merely wet. The road is not gritted above the second village and is impassable in snow.
```

**Chunk 3** — source: `guide_givens_mill.md#3` — produced by: `chunker.py::split_documents`

```
## Eat and drink

A tearoom attached to the mill, open 10 to 4 daily except Tuesdays, which sells bread made from the flour ground twenty metres away and is the reason most people come. One pub, food served lunchtimes and Thursday to Saturday evenings.
```

**Chunk 4** — source: `guide_kestrelford.md#6` — produced by: `chunker.py::split_documents`

```
## When to go

Late spring and early autumn. The Saturday market runs year-round but is much reduced from November to February. August is busy with walkers. The single-track approach road is genuinely difficult in snow and the town can be cut off for a day or two most winters.
```

**Chunk 5** — source: `guide_regional_transport.md#1` — produced by: `chunker.py::split_documents`

```
## The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

## Sample Answer

**Question:** How long is the Elder Ness shingle walk to the lighthouse?

**Answer:**

```
The Elder Ness shingle walk to the lighthouse takes 25 minutes.

Source: guide_walking.md (also mentioned in guide_elder_ness.md)
```

Sources retrieved: `guide_elder_ness.md`, `guide_halden_bay.md`, `guide_walking.md`

**My relevance cutoff:** 0.6 (the starter default, kept as is)

Ran my five questions and the five `OUT_OF_SCOPE` ones through `retrieve`,
top-k 5. Worst in-corpus distance was 0.452, best out-of-scope was 0.754.
Clean gap, no overlap. 0.6 sits right in the middle of that gap already, so
I didn't touch it.

| Question | In corpus? | Best distance |
|---|---|---|
| By what month do the coastal businesses begin closing and the days get short? | yes | 0.365 |
| What is the regional hub with 180,000 people? | yes | 0.452 |
| How long does driving from Brightwater to Corry Vale take on a good road? | yes | 0.314 |
| How long is the Elder Ness shingle walk to the lighthouse? | yes | 0.365 |
| If I am going to Halden Bay in August, what time should I arrive by? | yes | 0.256 |
| What is the capital of Mongolia? | no | 0.754 |
| How do I change the oil in a diesel engine? | no | 0.892 |
| Who won the 1994 World Cup? | no | 0.899 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.846 |
| How do I write a for loop in Rust? | no | 0.813 |

## How I Used AI

**1.** After writing the Milestone 3 chunker, I asked Claude to check my
chunker.py and README against the milestone's actual checklist before I
committed. It flagged that my rationale never cited the starter's real
baseline numbers (the `describe()` output), just my own city_guides
observation. I decided that was fine since city_guides was the only corpus
I touched — the other corpora's numbers (88/88, the 2-char chunk) aren't
mine to cite.

**2.** For `split_documents` in chunker.py, I asked Claude to help me work
out a header-splitting approach instead of the fixed-size window. I adjusted
the oversized-section fallback myself once I saw it was gluing paragraphs
together wrong.

**3.** For the Unit 2 improvement, I asked Claude to help me pick one. My
Diagnoses section said I missed nothing, so no failure pointed at a fix.
Claude walked through the options: a second chunking strategy had little room
because my chunker already splits on headers, and tuning the gate gained
nothing because 0.6 already sits in the gap between 0.452 and 0.754. It
suggested hybrid search because my criterion 1 rationale names exact figures
("35 minutes", "before 10am"), which is where keyword matching could help. It
also warned me up front that pass counts would probably not change, so I
should judge the result by where the answer chunk ranks. I made the final
call to go with hybrid search.

**4.** Claude wrote the first version of `store.py::_fuse_with_bm25`. When it
tested the function with `HYBRID` on and off, it found that the function could
push the nearest vector chunk out of the top 5, which raised the gate's best
distance on the first question from 0.365 to 0.462. Claude fixed that by
always keeping the top vector chunk, so the gate numbers stay comparable with
Before. Claude ran `run_eval.py --label after`, and I committed the results.

**5.** I asked Claude to review my Verdicts and Diagnoses. It noticed I had
"best in-corpus" and "worst out-of-scope" swapped in two places and fixed the
wording at my request. It also identified that the one After failure (Halden
Bay, "10 am" against "10am") came from the scorer's string match and not from
retrieval, and wrote that up as a scorer issue.

## Stretch: Metadata Filtering

`store.py::search` now takes a `source` argument and passes it to Chroma as
a `where={"source": ...}` filter, so a query can be scoped to one guide
instead of the whole corpus. Wired up as `--source FILENAME` on both
`app.py retrieve` and `app.py ask`.

Example: "How long is the walk to the lighthouse?" with no filter pulls its
best match (distance 0.391) from whichever guide covers it best. Add
`--source guide_halden_bay.md` and every result comes back restricted to
that one file, best distance 0.456. Worse, since it can't reach for the
guide that actually answers it best (Elder Ness), but correctly scoped.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks read as a complete thought | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. First named source actually contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Real output for each criterion, pasted as text from run 1 of
`results/run_2026-09-23_2103_before.md`. Criteria 3 and 4 are one
deterministic pass each (gate cutoff, and the 5 chunks sampled in Milestone 3),
so the same result stands for all three run columns.

**Criterion 1: retrieved chunk contains the answer.** Produced by
`store.py::search`, called from `run_eval.py::main`. Question: "What is the
regional hub with 180,000 people?" Best retrieved chunk, `guide_marchwood.md#0`,
distance 0.4517:

```
# Marchwood

Marchwood is the regional hub — 180,000 people, the junction everyone changes trains at, and a city most visitors pass through rather than stop in. That is a mistake, though an understandable one, since almost nothing of interest is near the station.
```

**Criterion 2: every answer names a source.** Produced by
`generate.py::answer_from_chunks`, called from `run_eval.py::main`. Run 1
answers, verbatim:

```
By November, the coastal businesses begin closing and the days are short (source: guide_seasons.md).
```

```
The regional hub with 180,000 people is Marchwood. This information comes from `guide_marchwood.md`.
```

```
Driving from Brightwater takes 35 minutes on a good road as far as the valley mouth.

Source: guide_corry_vale.md
```

```
The Elder Ness shingle walk to the lighthouse is 25 minutes long.

Sources: `guide_walking.md` and `guide_elder_ness.md`
```

```
If you are going to Halden Bay in August, you should arrive before 10am or plan to use the overflow lot (guide_seasons.md).
```

**Criterion 3: gate stops out-of-corpus questions.** Produced by
`run_eval.py::check_out_of_scope`, cutoff 0.6. Refused 5 of 5:

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.754 | refused |
| How do I change the oil in a diesel engine? | 0.892 | refused |
| Who won the 1994 World Cup? | 0.899 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.846 | refused |
| How do I write a for loop in Rust? | 0.813 | refused |

**Criterion 4: sampled chunks read as a complete thought.** Produced by
`chunker.py::split_documents`. One of the five sampled chunks
(`guide_corry_vale.md#6`, see Sample Chunks above), verbatim:

```
## When to go

May to September. Outside those months the pub in the third village closes, the farm shop reduces its hours, and several footpaths become genuinely boggy rather than merely wet. The road is not gritted above the second village and is impassable in snow.
```

**Criterion 5: first named source actually contains the answer.** Produced by
`generate.py::answer_from_chunks`, called from `run_eval.py::main`. Question:
"If I am going to Halden Bay in August, what time should I arrive by?" Run 1
answer names `guide_seasons.md` first:

```
If you are going to Halden Bay in August, you should arrive before 10am or plan to use the overflow lot (guide_seasons.md).
```

Sources retrieved for that run: guide_halden_bay.md, guide_marchwood.md,
guide_regional_transport.md, guide_seasons.md. Best distance 0.2558.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | Wanted 4/5, got 5/5 all three times. I went through `run_2026-09-23_2103_before.md` and for each of the five questions checked that the actual answer text showed up in the chunk that got retrieved — it did, every run. |
| 2 | Every answer names a source | MET | Wanted 5/5, got 5/5 all three times. Read all 15 answers (5 questions, 3 runs) and every single one ends with a `Source:` line or names the file inline. Never had to go looking for a citation. |
| 3 | Gate stops out-of-corpus questions | MET | Wanted 4/5, got 5/5 all three times, and honestly this one's a gimme — the cutoff is fixed and the questions are fixed, so `check_out_of_scope` gives the same result every run. Worst in-corpus distance was 0.452, best out-of-scope was 0.754. That's a wide gap, not a close call. |
| 4 | Sampled chunks read as a complete thought | MET | Wanted 4/5, got 5/5. Also deterministic — these are the same five chunks I sampled back in Milestone 3, so I just reread them and confirmed none of them cut off mid-thought. |
| 5 | First named source actually contains the answer | MET | Wanted 4/5, got 5/5 all three times. Went question by question and checked that the source named first in the answer matches the `expects` field in `questions.py`. It lined up every time, 15 for 15. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

Didn't miss anything, so no failure stages to trace here.

But I'll be honest — 4/5 was too soft a target for criteria 1, 3, 4, and 5. I
picked it because I expected at least one question to be flaky, but the corpus
is tiny (five short guides) and well-separated (0.452 worst in-corpus distance
vs. 0.754 best out-of-scope), so there wasn't really a failure mode that costs
you exactly one question. It either works or it doesn't, and three identical
5/5 runs back that up — no variance for the 4/5 buffer to actually catch.

If I redid it, I'd tighten criterion 1 to 5/5. It's the one that's actually
doing generation work every run instead of just replaying a fixed cutoff or a
pre-picked sample (that's 3 and 4), so three perfect runs there means the most.
It's also the one most likely to catch a real miss once the corpus gets bigger
than five documents.

## The Improvement

**What I changed:** Added hybrid search to `store.py::search`. It now pulls
the vector ranking for every chunk, builds a BM25 keyword ranking over the
same chunks (`store.py::_fuse_with_bm25`, `rank-bm25`), and merges the two with
reciprocal rank fusion (`1/(60+rank)` summed per chunk), then returns the top 5.
The relevance gate still reads cosine distance, and the nearest vector chunk is
always kept in the top 5, so `gate.py::check` sees the same best distance as
before. `config.HYBRID` switches it on and off. Nothing else changed: same
chunker, same corpus, same threshold, same prompt.

**Why I picked it:** Diagnoses found no miss, so nothing pointed at a fix. The
closest thing to a diagnosis is criterion 1's own rationale: my answers are
exact figures ("35 minutes", "before 10am"), which is where a keyword match
can help and meaning-only search can slide past. So this is a test of whether
that risk is real, not a repair.

### Run Log — After

From `results/run_2026-09-27_2105_after.md`. Criterion 3 is one deterministic
pass; criterion 4 is the same five sampled chunks, since the chunker did not
change.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks read as a complete thought | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. First named source actually contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Real output, run 1 of the After log. Produced by `run_eval.py::main` calling
`store.py::search` (hybrid) and `generate.py::answer_from_chunks`.

Question: "How long does driving from Brightwater to Corry Vale take on a good
road?" Retrieved chunks now put `guide_corry_vale.md` first (before, it was
second):

```
Best distance: 0.3137 (passed the gate)
Sources retrieved: guide_corry_vale.md, guide_kestrelford.md, guide_thornby_wells.md, guide_walking.md

Driving from Brightwater to the mouth of Corry Vale takes 35 minutes on a good road, plus 20 more minutes on a poor one.

Source: `guide_corry_vale.md`
```

The one scored failure, from the same file, "If I am going to Halden Bay in
August, what time should I arrive by?", run 1:

```
If you are going to Halden Bay in August, you should arrive before 10 am (source: guide_seasons.md).
```

**Did it help?** Not in any way the criteria can see. All five criteria came
out identical to Before, so the pass counts did not move. What did change is
ordering. For "35 minutes" the answer chunk moved from second to first in the
retrieved list, and for "November" the first chunk with the answer switched
from `guide_halden_bay.md` to `guide_seasons.md`, the better source. Lower
ranks also reshuffled: for the Marchwood question `guide_eating.md` and
`guide_seasons.md` dropped out and other Brightwater and Pellew Sands chunks
came in. Those swaps are noise-level on a five-document corpus.

The per-question score got slightly worse: 14 of 15 pass instead of 15 of 15.
That is not retrieval. The chunk was right and the model wrote "10 am" with a
space, and `scorer.py::judge` is a literal substring match against "before
10am". Runs 2 and 3 wrote "10am" and passed. I left the scorer alone because
this unit allows one change. So my honest read is: no measurable gain from
hybrid search on this corpus, a small cost in complexity, and one flaky
scorer/phrasing interaction that I only saw because I ran three times.

## What's Still Broken

No criterion is missed, so nothing is broken by my own standard. What is
still weak:

- **The scorer is brittle to formatting.** `scorer.py::judge` is a literal
  substring match. In the After run the model wrote "10 am" instead of
  "10am" once and the question scored fail (run 1, Halden Bay) even though
  the retrieved chunk and the source were right. I would normalise
  whitespace, or accept a list of forms per question. I did not change it
  because this unit allows only the one improvement, and doing it mid-unit
  would have changed what "Before" and "After" were measured with.
- **The targets are soft.** Criteria 1, 3, 4 and 5 all say 4 of 5 and every
  run came out 5 of 5. The 4/5 buffer never got tested. I would tighten
  criterion 1 to 5 of 5, as written in Diagnoses.
- **Hybrid search is unproven.** It did not change any pass count, and on a
  five-document corpus I cannot tell if it would matter at scale. I would
  test it on a bigger corpus, and log the rank of the answer chunk for every
  question, which `run_eval.py` does not do today.

I stopped here because every criterion passed, so there was nothing left that
my own tests told me to fix, and the remaining items need either a bigger
corpus or a second change.

## What I'd Do Differently

I would rewrite criteria 1, 4 and 5, and drop the 4-of-5 buffer.

- **Criterion 1** should be 5 of 5, and measure rank: "the answer chunk is in
  the top 3." Retrieval is deterministic here, so a buffer of one miss only
  hides a problem. Top 3 would also be a check hybrid search could actually move.
- **Criterion 4** ("4 of 5 sampled chunks read as a complete thought") is
  subjective and I sampled the same five chunks every time, so it cannot
  vary. I would make it countable, for example "no chunk ends mid-sentence
  across all chunks", checked by script.
- **Criterion 5** is checked by hand against the `expects` field. I would
  make it automatic with a check of the first cited source against a
  `source` field per question.

All three passed on the first try, which tells me they were safe, not that
the system is excellent.
