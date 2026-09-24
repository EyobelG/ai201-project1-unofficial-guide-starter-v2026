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
top-k 5. Best in-corpus distance was 0.452, worst out-of-scope was 0.754.
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

Produced by `run_eval.py::main` and `run_eval.py::check_out_of_scope`, from
`results/run_2026-09-23_2103_before.md`. Criteria 3 and 4 are one
deterministic pass each (gate cutoff, and the 5 chunks sampled in Milestone 3),
so the same number is repeated across the three run columns.

Question by question, all three runs (5/5 each time):

```
By what month do the coastal businesses begin closing and the days get short?
  -> By November, the coastal businesses begin closing and the days are short
     (source: guide_seasons.md).
What is the regional hub with 180,000 people?
  -> The regional hub with 180,000 people is Marchwood. This information
     comes from `guide_marchwood.md`.
How long does driving from Brightwater to Corry Vale take on a good road?
  -> Driving from Brightwater takes 35 minutes on a good road as far as the
     valley mouth. Source: guide_corry_vale.md
How long is the Elder Ness shingle walk to the lighthouse?
  -> The Elder Ness shingle walk to the lighthouse is 25 minutes long.
     Sources: `guide_walking.md` and `guide_elder_ness.md`
If I am going to Halden Bay in August, what time should I arrive by?
  -> If you are going to Halden Bay in August, you should arrive before 10am
     or plan to use the overflow lot (guide_seasons.md).
```

Out-of-scope gate (`run_eval.py::check_out_of_scope`), refused 5 of 5:

```
What is the capital of Mongolia?            best distance 0.754  refused
How do I change the oil in a diesel engine? best distance 0.892  refused
Who won the 1994 World Cup?                 best distance 0.899  refused
What is the recommended dosage of ibuprofen for a headache? 0.846  refused
How do I write a for loop in Rust?          best distance 0.813  refused
```

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
| 3 | Gate stops out-of-corpus questions | MET | Wanted 4/5, got 5/5 all three times, and honestly this one's a gimme — the cutoff is fixed and the questions are fixed, so `check_out_of_scope` gives the same result every run. Best in-corpus distance was 0.452, worst out-of-scope was 0.754. That's a wide gap, not a close call. |
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

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
