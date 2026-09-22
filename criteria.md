# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->
All 5 questons have a very specific answer that is not ambiguous, and the
corpus is small enough that the answer should be in at least one chunk.
I allow one miss (4 of 5, not 5 of 5) because my questions depend on exact
figures ("35 minutes", "before 10am") that a chunk boundary could split from
their sentence; I don't go lower because with TOP_K = 5 retrieved chunks, missing
2 of 5 would mean the embedder itself is failing, not just one bad boundary.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->
This is because the corpus is small and the questions are specific enough that
the answer should be in at least one chunk, and the system is designed to 
always include a source if it finds an answer.
All five, not four: naming a source is mechanical (the pipeline attaches the
retrieved document), so a single answer without one means a bug in the code,
not a hard question. There is no acceptable miss rate for a bug.
---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->
My out-of-scope questions (Mongolia, diesel engines, the World Cup, ibuprofen,
Rust) have nothing in common with a corpus of fictional coastal towns, so I
expect them to sit far from every chunk. I picked 4 of 5 rather than 5 of 5
because a cutoff that is loose enough to keep in-scope questions answerable may
let one stray question through, and rather than 3 of 5 because a gate that lets
two off-topic questions reach the model is not really a gate. I haven't
measured distances yet (Milestone 4), so this may need diagnosing later.

---

## 4. Something about your chunks

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

When I sample 5 chunks, at least 4 of them read as a complete thought, with no
sentence cut in half at either end.

**Why this target:**
Chunks are 800 characters with 120 overlap (config.py), and documents are
prose, so a fixed-size split can land mid-sentence. I picked 4 of 5 rather
than 5 of 5 because overlap means a cut at the edge is sometimes fine, and one
ragged chunk in a sample of five is tolerable. I did not pick 3 of 5 because if
two in five are cut mid-thought, the chunker is losing answers such as "25
minutes" from the sentence that explains them.



---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->
For at least 4 of my 5 test questions, the first source the system names is a
document that actually contains the answer (checked by opening the document and
finding the `expects` phrase in it), not merely any document that was retrieved.

**Why this target:**
Criterion 2 only checks that a source is named, which a wrong source would also
pass. Correct attribution is what makes the answer trustworthy to a visitor.
I set it to match criterion 1 (4 of 5) because a right source should follow
from a right chunk; I did not set 5 of 5 because a question whose answer
appears in several documents could name a different, still-valid one.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
