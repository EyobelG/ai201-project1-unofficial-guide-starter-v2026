"""
Unit 2: decide whether an answer is correct.

`run_eval.py` imports this file and calls `judge` on every run. If this file
doesn't exist, or `judge` isn't found with this exact name and signature, the
Run columns come out blank and nothing is broken — it just means run_eval.py
is running unscored.
"""

import gate


def judge(question: str, expects: str, answer: str, results) -> bool:
    """True if `answer` contains `expects` (case-insensitive) and isn't a refusal.

    A literal substring check, not a fuzzy one: every `expects` in
    questions.py is a short, exact fact ("35 minutes", "Marchwood"), so an
    answer that states it will contain that exact string. An answer that
    paraphrases the fact away from that string is not one I wrote the
    question to expect.
    """
    expects = (expects or "").strip()
    if not expects:
        return False
    answer = (answer or "").strip()
    if answer == gate.REFUSAL:
        return False
    return expects.lower() in answer.lower()
